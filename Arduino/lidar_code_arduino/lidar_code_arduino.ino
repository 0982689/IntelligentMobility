int arraySize = 15;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int arrayData[arraySize] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
  for(int i = 0; i < arraySize-1;i++){
    Serial.print(arrayData[i]);
    Serial.print(",");
  } 
  Serial.print(arrayData[arraySize-1]);
  Serial.println();
  delay(1000);
}
