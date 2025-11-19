#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h> // 
#include <LMP91000.h>
#include "ADS1X15.h"
#include "bitmapsLarges.h"
// mosquitto -v -c mosquitto.conf

#include "SPI.h"
#include "TFT_eSPI.h"
TFT_eSPI tft = TFT_eSPI();

#define WIFI_SSID "roboticai"
#define WIFI_PASSWORD "20255202"
#define mqtt_server "10.1.2.100"

WiFiClient espClient;
PubSubClient client(espClient);
LMP91000 lmp = LMP91000();
ADS1115 ADS(0x49);

const double v_tolerance = 33;
byte moc1,moc2,moc3,moc4;
int S_Vol,E_Vol,Step,Freq,Cycle;
String chuoi="",chuoi1,chuoi2,chuoi3,chuoi4,chuoi5,stt_cm,outlcd,cm,imax,imin,dtu,preoutlcd;

void callback(char* topic, byte* message, unsigned int length)
{
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++)
  {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  if (String(topic) == "CV/statusESP")
  {
    if(messageTemp == "checking") client.publish("CV/statusESP", "ready");
    else if(messageTemp == "restart") ESP.restart();
  }
  if (String(topic) == "CV/status_plot")
  {
    if(messageTemp == "run") stt_cm = messageTemp;
  }
  if (String(topic) == "CV/command") chuoi=messageTemp;
  if (String(topic) == "CV/lcd") outlcd=messageTemp;
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client"))
    {
      Serial.println("connected");
      client.subscribe("CV/status_plot");
      client.subscribe("CV/statusESP");
      client.subscribe("CV/command");
      client.subscribe("CV/lcd");
      for (int i = 1; i <= 5; i++) {
        client.subscribe("CV/min_v_" + i);
        client.subscribe("CV/max_v_" + i);
        client.subscribe("CV/min_a_" + i);
        client.subscribe("CV/max_v_" + i);
        client.subscribe("CV/delta_v_" + i);
        client.subscribe("CV/cm_" + i);
      }
      client.publish("CV/statusESP", "ready");
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
  
void setup()
{
  Wire.begin();
  Serial.begin(115200);

  pinMode(25, INPUT);

  tft.init();
  tft.fillScreen(TFT_BLACK);
  int w = tft.width(),h  = tft.height(), row, col, buffidx=0;
  for (col=0; col<w; col++) { // For each scanline...
    for (row=h-1; row>=0; row--) { // For each pixel...
      tft.drawPixel(col, row, pgm_read_word(evive_in_hand + buffidx));
      buffidx++;
    }
  }
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("connecting");
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("connected: ");
  Serial.println(WiFi.localIP());

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  client.subscribe("CV/values");
  client.subscribe("CV/status_plot");
  client.subscribe("CV/statusESP");
  client.subscribe("CV/lcd");
  client.publish("CV/statusESP", "ready");
  
  analogSetPinAttenuation(33, ADC_0db);
  delay(500);
  lmp.standby();
  delay(500);
  initLMP();
  initASD();
  delay(2000);
}


void loop() 
{
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  if (digitalRead(25)==HIGH) client.publish("CV/wirelessact", "start");
  if (stt_cm=="run")
  {    
    Serial.println(chuoi);    
    for(int i=0;i<chuoi.length();i++){
      if(chuoi.charAt(i)=='|'){
        moc1=i;
        }
      if(chuoi.charAt(i)=='_'){
        moc2=i;
        }       
      if(chuoi.charAt(i)=='?'){
        moc3=i;
        }
      if(chuoi.charAt(i)=='#'){
        moc4=i;
        }                
      }
      chuoi1=chuoi;
      chuoi2=chuoi;
      chuoi1.remove(moc1);
      chuoi2.remove(0,moc1+1);
      chuoi3=chuoi2;
      chuoi2.remove(moc2-moc1-1);
      chuoi3.remove(0,moc2-moc1);
      chuoi4=chuoi3;
      chuoi3.remove(moc3-moc2-1);
      chuoi4.remove(0,moc3-moc2);
      chuoi5=chuoi4;
      chuoi4.remove(moc4-moc3-1);
      chuoi5.remove(0,moc4-moc3);

      S_Vol=chuoi1.toInt();
      E_Vol=chuoi2.toInt();
      Step=chuoi3.toInt();
      Freq=chuoi4.toInt();
      Cycle=chuoi5.toInt();

  int i=0;
  while(i<Cycle)
  {
         runCV(S_Vol, E_Vol, Step, Freq);
         runCV(E_Vol, S_Vol, Step, Freq);
         i++;
  }
  stt_cm = "done";
  client.publish("CV/status_plot", stt_cm.c_str());
  }
  if (outlcd!=preoutlcd){
    text();
    outlcd=preoutlcd;
  }
}

void initLMP()
{
  lmp.disableFET(); 
  lmp.setGain(2); // 3.5kOhm
  lmp.setRLoad(0); //10Ohm
  lmp.setIntRefSource(); //Sets the voltage reference source to supply voltage (Vdd).
  lmp.setIntZ(0); //V(Iz) = 0.2*Vdd
  lmp.setThreeLead(); //3-lead amperometric cell mode                  
}

void initASD()
{
  ADS.begin();
  ADS.setGain(1);      //  6.144 volt
//  ADS.setMode(0);      //  continuous mode
}

void runCV(int16_t startV, int16_t endV, int16_t stepV, double freq)

{
  stepV = abs(stepV);
  freq = (uint16_t)(1000.0 / (2*freq));


  if(startV < endV) runCVForward(startV, endV, stepV, freq);
  else runCVBackward(startV, endV, stepV, freq);

}

void setBiasVoltage(int16_t voltage)
{
  //define bias sign
  if(voltage < 0) lmp.setNegBias();
  else if (voltage > 0) lmp.setPosBias();
  else {} //do nothing

  //define bias voltage
  uint16_t Vdd = 3300;
  uint8_t set_bias = 0; 

  int16_t setV = Vdd*TIA_BIAS[set_bias];
  voltage = abs(voltage);

  while(setV > voltage+v_tolerance || setV < voltage-v_tolerance)
  {
    set_bias++;
    if(set_bias > NUM_TIA_BIAS) return;  //if voltage > 0.825 V

    setV = Vdd*TIA_BIAS[set_bias];
  }

  lmp.setBias(set_bias); 
}

void biasAndSample(int16_t voltage, double rate)
{
  //Serial.print("Time(ms): "); Serial.print(millis()); 
  //Serial.print(", Voltage(mV): ");
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  long int t1 = millis();
//  Serial.print(voltage);

  setBiasVoltage(voltage);
  int16_t val_0 = ADS.readADC(0);  
  int16_t val_1 = ADS.readADC(1);
  
  float temp = lmp.getVoltage(val_0, 3.3, 14);
  float amperage = (temp - 1) / 7000;
  float amp = amperage/pow(10,-6);
  //Serial.print(", Vout(V): ");
  //Serial.print(tensao,5);
  //Serial.print(", Current(uA): ");
  //Serial.print(",");
//  Serial.print("|");
//  String values = String(voltage) + ";" + String(amp) + ";" + String(millis()-t1);
  client.publish("CV/values",String(String(voltage) + ";" + String(amp) + ";" + String(millis()-t1)).c_str());
//  Serial.print(";");
//  Serial.println(amperage/pow(10,-6),5);
//Serial.print(voltage); Serial.print(","); Serial.print(millis()-t1);Serial.print(","); Serial.println(rate);
  delay(rate);
  
}

void runCVForward(int16_t startV, int16_t endV, int16_t stepV, double freq)

{
  for (int16_t j = startV; j <= endV; j += stepV)
  {
    biasAndSample(j,freq);
  }
}


void runCVBackward(int16_t startV, int16_t endV, int16_t stepV, double freq)

{
  for (int16_t j = startV; j >= endV; j -= stepV)
  {
    biasAndSample(j,freq);
  }
}

void text()
{
  Serial.println(outlcd);
  for(int i=0;i<outlcd.length();i++){
      if(outlcd.charAt(i)=='|'){
        moc1=i;}
      if(outlcd.charAt(i)=='_'){
        moc2=i;}
      if(outlcd.charAt(i)=='?')
        moc3=i;}
  cm=outlcd;
  imax=outlcd;
  cm.remove(moc1);
  imax.remove(0,moc1+1);
  imin=imax;
  imax.remove(moc2-moc1-1);
  imin.remove(0,moc2-moc1);
  dtu=imin;
  imin.remove(moc3-moc2-1);
  dtu.remove(0,moc3-moc2);
  
  tft.setRotation(3);
  tft.fillRect(125,65,150,20,ILI9341_WHITE);
  tft.setCursor(130, 69);
  tft.setTextColor(TFT_GREEN);
  tft.setTextSize(2.75);
  tft.println(cm);

  tft.fillRect(125,110,150,20,ILI9341_WHITE);
  tft.setCursor(130, 114);
  tft.setTextColor(TFT_GREEN);
  tft.setTextSize(2.75);
  tft.println(imax+"(A)");

  tft.fillRect(125,154,150,20,ILI9341_WHITE);
  tft.setCursor(130, 158);
  tft.setTextColor(TFT_GREEN);
  tft.setTextSize(2.75);
  tft.println(imin+"(A)");

  tft.fillRect(125,202,150,20,ILI9341_WHITE);
  tft.setCursor(130, 206);
  tft.setTextColor(TFT_GREEN);
  tft.setTextSize(2.75);
  tft.println(dtu+"(V)");
}
