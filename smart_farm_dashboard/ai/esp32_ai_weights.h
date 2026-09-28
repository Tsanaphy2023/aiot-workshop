/* Auto-generated Smart Farm AI Model for ESP32 */
#ifndef SMART_FARM_AI_MODEL_H
#define SMART_FARM_AI_MODEL_H

const int AI_INPUT_DIM = 4;
const int AI_HIDDEN_DIM = 8;
const int AI_OUTPUT_DIM = 2;

const float W1[4][8] = {
  {0.08787f, -0.15359f, 0.16962f, -0.09615f, 0.17939f, 0.07359f, -0.15737f, -0.20140f},
  {0.08253f, -0.37855f, -0.25358f, 0.02603f, -0.48752f, -0.32599f, -0.09836f, -0.30222f},
  {0.14948f, 0.13591f, 0.05289f, -0.23494f, -0.06964f, 0.28159f, -0.11456f, 0.37786f},
  {-0.20268f, -0.43245f, -0.01895f, 0.17604f, 0.25282f, -0.10903f, 0.07537f, 0.32581f},
};

const float W2[8][2] = {
  {0.13519f, -0.06252f},
  {0.09466f, 0.21845f},
  {0.40162f, -0.45011f},
  {-0.09061f, -0.44973f},
  {0.36874f, 0.37763f},
  {-0.08479f, -0.23026f},
  {-0.40666f, -0.43341f},
  {0.41905f, 0.05538f},
};

#endif // SMART_FARM_AI_MODEL_H
