/*
 * Functions.c
 *
 *  Created on: 01.03.2020
 *      Author: T.Burkard
 */

#include "Functions.h"

/************************* Global Variables ***********************/

extern uint16_t Encoder_Counter[];
extern int8_t   Encoder_Sign[];

extern uint8_t USBreceivedBuffer[];


/************************** Init Functions ************************/

void TIM_Init(TIM_HandleTypeDef htim2, TIM_HandleTypeDef htim3)
{
	// Initialize TIM2 for Encoder left & right
	htim2.Instance->DIER  = 0x07;               // Enable Input Capture CH1/2 Interrupt and Update Interrupt
	htim2.Instance->CCMR1 = (1<<0) | (1 << 8);  // Capture/Compare 1/2 Selection: CC1/2 channel is configured as input, IC1/2 is mapped on TI1/2
	htim2.Instance->CCER  = (1<<0) | (1<<4);    // Capture/compare 1/2 enable
	htim2.Instance->CR1   = 0x01;               // Enable and start Timer

	// Initialize TIM3 for Motor PWM Output left & right
	htim3.Instance->CR1   |= (1<<9);                      // CKD: 4x clock division
	htim3.Instance->PSC    = 16;                          // Prescaler: 16 + 1 = 17
	htim3.Instance->CR1   |= (1<<7);                      // ARPE: Auto-repload preload enable
	htim3.Instance->CCMR1 |= (1<<6) | (1<<5) | (1<<3);	  // Bit5,6: PWM mode 1, Bit3: OC1PE output compare 1 preload enable -> CCR1 preload value is loaded in the active register at each update event
	htim3.Instance->CCMR1 |= (1<<14) | (1<<13) | (1<<11); // Bi13,14: PWM mode 1, Bit11: OC2PE output compare 2 preload enable -> CCR2 preload value is loaded in the active register at each update event
	htim3.Instance->CCER  |= (1<<0);                      // CC1E: enable capture/compare 1 output -> OC1 signal is output on the corr. output pin
	htim3.Instance->CCER  |= (1<<4);                      // CC2E: enable capture/compare 2 output -> OC2 signal is output on the corr. output pin
	htim3.Instance->CCR1   = MOTOR_CCR_VALUE_OFFS;
	htim3.Instance->CCR2   = MOTOR_CCR_VALUE_OFFS;
	htim3.Instance->ARR    = 0xFFFF;                      // Auto Reload register
	htim3.Instance->CR2    = (1<<4);                      // Enable CNT_EN as trigger output (TRGO)
	htim3.Instance->EGR    = (1<<0);                      // Re-initialize the counter and generate an update of the registers.
	htim3.Instance->CR1   |= 0x01;                        // Enable and start Timer
}


/************************* Sensor Functions ***********************/

void IMU_calibrate_offset(int8_t* IMU_OffsetCalibration, const uint8_t* ADCbuffer)
{
	// The difference of the ADC-Value and the expected ADC-Value at 0g resp. 1g is stored in the IMU_OffsetCalibration-Array
	IMU_OffsetCalibration[X_AXIS] = ADCbuffer[X_AXIS] - IMU_ADCVALUE_0g;
	IMU_OffsetCalibration[Y_AXIS] = ADCbuffer[Y_AXIS] - IMU_ADCVALUE_0g;
	IMU_OffsetCalibration[Z_AXIS] = ADCbuffer[Z_AXIS] - IMU_ADCVALUE_1g;
}

void Encoder_calculateDeltaValue(uint32_t* Encoder_DeltaValue)
{
	// Encoder left
	if(Encoder_Counter[LEFT] == 0)
	{
		// means there was no Timer-Interrupt since the last call of this function -> it has to be assumed that the wheel is not turning anymore
		Encoder_DeltaValue[LEFT] = 0xFFFFFFFF;
	}
	else
	{
		Encoder_DeltaValue[LEFT] = ENCODER_MEASUREMENT_TIME / Encoder_Counter[LEFT];
	}
	Encoder_Counter[LEFT] = 0;  // reset Encoder Count

	// Encoder right
	if(Encoder_Counter[RIGHT] == 0)
	{
		// means there was no Timer-Interrupt since the last call of this function -> it has to be assumed that the wheel is not turning anymore
		Encoder_DeltaValue[RIGHT] = 0xFFFFFFFF;
	}
	else
	{
		Encoder_DeltaValue[RIGHT] = ENCODER_MEASUREMENT_TIME / Encoder_Counter[RIGHT];
	}
	Encoder_Counter[RIGHT] = 0;  // reset Encoder Count
}

void Encoder_calculateSpeed(int16_t* Encoder_Speed)
{
	uint32_t Encoder_DeltaValue[2];  // in [us]

	Encoder_calculateDeltaValue(Encoder_DeltaValue);

	Encoder_Speed[LEFT]  = DISTANCE_PER_STEP * 1000000 / Encoder_DeltaValue[LEFT] * Encoder_Sign[LEFT];   // [mm] * 1'000'000 / [us] = [mm/s]
	Encoder_Speed[RIGHT] = DISTANCE_PER_STEP * 1000000 / Encoder_DeltaValue[RIGHT] * Encoder_Sign[RIGHT]; // [mm] * 1'000'000 / [us] = [mm/s]
}

uint16_t DistanceSensor_convert(uint8_t ADC_DistanceValue)
{
	return (uint16_t)(ADC_DistanceValue * 3.3f / 0xFF * (-634) + 1754);  // L(u) = mU + b, m = -634, b = 1745, [L] = mm, [u] = V
}


/************** USB prepair SensorDataBuff Functions **************/

void USB_prepair_SensorDataBuffer_IMU(uint8_t* SensorDataBuffer, const uint8_t* ADCbuffer, const int8_t* IMU_OffsetCalibration)
{
	SensorDataBuffer[0] = ((int16_t)(ADCbuffer[X_AXIS] - IMU_OffsetCalibration[X_AXIS] - IMU_ADCVALUE_0g) * (int16_t)CONVERT_TO_MILLI_G) >> 8;	 // IMU value X-Axis HighByte
	SensorDataBuffer[1] = ((int16_t)(ADCbuffer[X_AXIS] - IMU_OffsetCalibration[X_AXIS] - IMU_ADCVALUE_0g) * (int16_t)CONVERT_TO_MILLI_G) & 0xFF; // IMU value X-Axis LowByte

	SensorDataBuffer[2] = ((int16_t)(ADCbuffer[Y_AXIS] - IMU_OffsetCalibration[Y_AXIS] - IMU_ADCVALUE_0g) * (int16_t)CONVERT_TO_MILLI_G) >> 8;	 // IMU value Y-Axis HighByte
	SensorDataBuffer[3] = ((int16_t)(ADCbuffer[Y_AXIS] - IMU_OffsetCalibration[Y_AXIS] - IMU_ADCVALUE_0g) * (int16_t)CONVERT_TO_MILLI_G) & 0xFF; // IMU value Y-Axis LowByte

	SensorDataBuffer[4] = ((int16_t)(ADCbuffer[Z_AXIS] - IMU_OffsetCalibration[Z_AXIS] - IMU_ADCVALUE_0g) * (int16_t)CONVERT_TO_MILLI_G) >> 8;	 // IMU value Z-Axis HighByte
	SensorDataBuffer[5] = ((int16_t)(ADCbuffer[Z_AXIS] - IMU_OffsetCalibration[Z_AXIS] - IMU_ADCVALUE_0g) * (int16_t)CONVERT_TO_MILLI_G) & 0xFF; // IMU value Z-Axis LowByte
}

void USB_prepair_SensorDataBuffer_Encoder(uint8_t* SensorDataBuffer, const int16_t* Encoder_Speed)
{
	SensorDataBuffer[6] = (Encoder_Speed[LEFT]) >> 8;	 // Encoder left HighByte
	SensorDataBuffer[7] = (Encoder_Speed[LEFT]) & 0xFF;  // Encoder left LowByte

	SensorDataBuffer[8] = (Encoder_Speed[RIGHT]) >> 8;	 // Encoder right HighByte
	SensorDataBuffer[9] = (Encoder_Speed[RIGHT]) & 0xFF; // Encoder right LowByte
}

void USB_prepair_SensorDataBuffer_DistanceSensor(uint8_t* SensorDataBuffer, const uint8_t* ADCbuffer)
{
	SensorDataBuffer[10] = DistanceSensor_convert(ADCbuffer[3]) >> 8;	// DistanceSensor straight HighByte
	SensorDataBuffer[11] = DistanceSensor_convert(ADCbuffer[3]) & 0xFF;	// DistanceSensor straight LowByte

	SensorDataBuffer[12] = DistanceSensor_convert(ADCbuffer[4]) >> 8;	// DistanceSensor tilted HighByte
	SensorDataBuffer[13] = DistanceSensor_convert(ADCbuffer[4]) & 0xFF;	// DistanceSensor tilted LowByte
}


/*********************** USB send Functions ***********************/

void USB_send_Command(uint8_t Cmd, uint8_t* dataBuffer, uint8_t dataSize)
{
	uint8_t USBsendBuffer[dataSize + 1];

	USBsendBuffer[0] = Cmd;

	for(uint8_t i = 0; i < dataSize; i++)
	{
		USBsendBuffer[i+1] = dataBuffer[i];
	}

	CDC_Transmit_FS(USBsendBuffer, dataSize + 1);
}

void USB_send_start(void)
{
	USB_send_Command(USB_CMD_START, NULL, 0);
}

void USB_send_stop(void)
{
	USB_send_Command(USB_CMD_STOP, NULL, 0);
}

void USB_send_sensordata(const uint8_t* ADCbuffer, const int8_t* IMU_OffsetCalibration, const int16_t* Encoder_Speed)
{
	uint8_t SensorDataBuffer[USB_CMD_DATASIZE_SENSORDATA];

	// prepair IMU data
	USB_prepair_SensorDataBuffer_IMU(SensorDataBuffer, ADCbuffer, IMU_OffsetCalibration);

	// prepair Encoder data
	USB_prepair_SensorDataBuffer_Encoder(SensorDataBuffer, Encoder_Speed);

	// prepair DistanceSensor data
	USB_prepair_SensorDataBuffer_DistanceSensor(SensorDataBuffer, ADCbuffer);

	USB_send_Command(USB_CMD_SENSORDATA, SensorDataBuffer, USB_CMD_DATASIZE_SENSORDATA);
}


/********************* USB receive Function ***********************/

void USB_receive_handle(int16_t* Motor_TargetSpeedReceived, uint16_t MainCounter, bool* Buzzer_ActiveFlag, uint16_t* Buzzer_ResetCounter, bool* JetsonReady)
{
	int16_t Motor_TargetSpeedMean;
	int16_t Motor_TargetSpeedAngle;

	switch(USBreceivedBuffer[0])
	{
		case USB_CMD_START:
		{
			*JetsonReady = true;

			// Notify user by a short beep
			buzzer_initiate_shortbeep(Buzzer_ActiveFlag, MainCounter, Buzzer_ResetCounter);

			break;
		}

		case USB_CMD_STOP:
	    {
		    *JetsonReady = false;

			// Notify user by a short beep
			buzzer_initiate_shortbeep(Buzzer_ActiveFlag, MainCounter, Buzzer_ResetCounter);

			Motor_TargetSpeedReceived[LEFT]  = 0;
			Motor_TargetSpeedReceived[RIGHT] = 0;

		    break;
	    }

		case USB_CMD_TARGETVECTOR:
		{
			// Decode received USB data
			Motor_TargetSpeedMean  = USBreceivedBuffer[2] + (((int16_t)(USBreceivedBuffer[1]))<<8);
			Motor_TargetSpeedAngle = USBreceivedBuffer[4] + (((int16_t)(USBreceivedBuffer[3]))<<8);

			// Limit Angle
			Motor_TargetSpeedAngle = Motor_TargetSpeedAngle > MOTOR_ANGLE_MAX ? MOTOR_ANGLE_MAX : Motor_TargetSpeedAngle;
			Motor_TargetSpeedAngle = Motor_TargetSpeedAngle < MOTOR_ANGLE_MIN ? MOTOR_ANGLE_MIN : Motor_TargetSpeedAngle;

			if(Motor_TargetSpeedAngle >= 0)
			{
				// Means Target Direction is right
				if(Motor_TargetSpeedMean != 0)
				{
					Motor_TargetSpeedReceived[RIGHT] = 2 * Motor_TargetSpeedMean * (90 - Motor_TargetSpeedAngle) / (180 - Motor_TargetSpeedAngle);
					Motor_TargetSpeedReceived[LEFT]  = 2 * Motor_TargetSpeedMean - Motor_TargetSpeedReceived[RIGHT];
				}
				else
				{
					// If speed is = 0 and angel is != 0, the vehicle turns on the spot, the speed of turn depends on the required angle
					Motor_TargetSpeedReceived[RIGHT] = Motor_TargetSpeedAngle * 10;
					Motor_TargetSpeedReceived[LEFT]  = -Motor_TargetSpeedReceived[RIGHT];
				}
			}
			else
			{
				// Means Target Direction is left
				if(Motor_TargetSpeedMean != 0)
				{
					Motor_TargetSpeedReceived[LEFT]  = 2 * Motor_TargetSpeedMean * (90 + Motor_TargetSpeedAngle) / (180 + Motor_TargetSpeedAngle);
					Motor_TargetSpeedReceived[RIGHT] = 2 * Motor_TargetSpeedMean - Motor_TargetSpeedReceived[LEFT];
				}
				else
				{
					// If speed is = 0 and angel is != 0, the vehicle turns on the spot, the speed of turn depends on the required angle
					Motor_TargetSpeedReceived[RIGHT] = Motor_TargetSpeedAngle * 10;
					Motor_TargetSpeedReceived[LEFT]  = -Motor_TargetSpeedReceived[RIGHT];
				}
			}

			// limit max TargetSpeed left
			if(Motor_TargetSpeedReceived[LEFT] > MOTOR_SPEED_MAX)
			{
				Motor_TargetSpeedReceived[LEFT] = MOTOR_SPEED_MAX;
			}
			else if(Motor_TargetSpeedReceived[LEFT] < MOTOR_SPEED_MIN)
			{
				Motor_TargetSpeedReceived[LEFT] = MOTOR_SPEED_MIN;
			}

			// limit max TargetSpeed right
			if(Motor_TargetSpeedReceived[RIGHT] > MOTOR_SPEED_MAX)
			{
				Motor_TargetSpeedReceived[RIGHT] = MOTOR_SPEED_MAX;
			}
			else if(Motor_TargetSpeedReceived[RIGHT] < MOTOR_SPEED_MIN)
			{
				Motor_TargetSpeedReceived[RIGHT] = MOTOR_SPEED_MIN;
			}

			break;
	    }

		case USB_CMD_PLAYAUDIO:
		{
			if(USBreceivedBuffer[1] == USB_CMD_PLAYAUDIO_SHORTBEEP)
			{
				// short beep
				buzzer_initiate_shortbeep(Buzzer_ActiveFlag, MainCounter, Buzzer_ResetCounter);
			}
			else if(USBreceivedBuffer[1] == USB_CMD_PLAYAUDIO_LONGBEEP)
			{
				// long beep
				buzzer_initiate_longbeep(Buzzer_ActiveFlag, MainCounter, Buzzer_ResetCounter);

			}

			break;
		}

	    case USB_CMD_LED:
	    {
		   if(USBreceivedBuffer[1] == 0)
		   {
			   led_off();
		   }
		   else if(USBreceivedBuffer[1] == 1)
		   {
		   	   led_on();
		   }

		   break;
	    }

	    default: // unknown Command
	    {
		    // TODO
	    	buzzer_initiate_longbeep(Buzzer_ActiveFlag, MainCounter, Buzzer_ResetCounter);

		    break;
	    }
    }
}


/******* smoothly adjust TargetSpeed to TargetSpeedReceived*******/

void adjust_TargetSpeed(int16_t* Motor_TargetSpeed, int16_t* Motor_TargetSpeedReceived)
{
	static int16_t Motor_TargetSpeed_old[2] = {0, 0};  // values from the iteration before

	// In order to not strain the mechanics too much, the allowed max. step of the target speed value is limited
	//  -> for that, a max. step limit of 100 mm/s each iteration (i.e. each 100 ms) is implemented

	// Target value left
	Motor_TargetSpeed[LEFT] = Motor_TargetSpeedReceived[LEFT];
	if((Motor_TargetSpeed[LEFT] - 100) > Motor_TargetSpeed_old[LEFT])
	{
		Motor_TargetSpeed[LEFT] = Motor_TargetSpeed_old[LEFT] + 100;
	}
	else if((Motor_TargetSpeed[LEFT] + 100) < Motor_TargetSpeed_old[LEFT])
	{
		Motor_TargetSpeed[LEFT] = Motor_TargetSpeed_old[LEFT] - 100;
	}

	// Target value right
	Motor_TargetSpeed[RIGHT] = Motor_TargetSpeedReceived[RIGHT];
	if((Motor_TargetSpeed[RIGHT] - 100) > Motor_TargetSpeed_old[RIGHT])
	{
		Motor_TargetSpeed[RIGHT] = Motor_TargetSpeed_old[RIGHT] + 100;
	}
	else if((Motor_TargetSpeed[RIGHT] + 100) < Motor_TargetSpeed_old[RIGHT])
	{
		Motor_TargetSpeed[RIGHT] = Motor_TargetSpeed_old[RIGHT] - 100;
	}

	// Update old values for next iteration
	Motor_TargetSpeed_old[LEFT]  = Motor_TargetSpeed[LEFT];
	Motor_TargetSpeed_old[RIGHT] = Motor_TargetSpeed[RIGHT];

}

/********************** Buzzer Functions **************************/

void buzzer_initiate_longbeep(bool* Buzzer_ActiveFlag, uint16_t MainCounter, uint16_t* Buzzer_ResetCounter)
{
	buzzer_on();
	*Buzzer_ActiveFlag = 1;
	*Buzzer_ResetCounter = MainCounter + BUZZER_LONGBEEP_DURATION;
}

void buzzer_initiate_shortbeep(bool* Buzzer_ActiveFlag, uint16_t MainCounter, uint16_t* Buzzer_ResetCounter)
{
	buzzer_on();
	*Buzzer_ActiveFlag = 1;
	*Buzzer_ResetCounter = MainCounter + BUZZER_SHORTBEEP_DURATION;
}


/************************ Motor Control ***************************/
void Motor_Control(TIM_HandleTypeDef htim,const int16_t* Encoder_Speed,const int16_t* Motor_TargetSpeed)
{
	uint32_t CCR_Value[2] = {0, 0};  // Total CCR-Value, which is going to be applied to the PWM-Timer

	uint32_t CCR_Value_Preset[2]  = {0, 0};
	int32_t  CCR_Value_P[2]       = {0, 0};
	static int32_t CCR_Value_I[2] = {0, 0};

	static uint16_t CounterLeft  = 0;
	static uint16_t CounterRight = 0;

	static t_motor_backwardState Motor_BackwardState[2] = {none, none};

	// check if motor does not need to turn backwards anymore
	if((Motor_TargetSpeed[LEFT] >= 0) && (Motor_BackwardState[LEFT] == backward)) { Motor_BackwardState[LEFT] = none; }
	if((Motor_TargetSpeed[RIGHT] >= 0) && (Motor_BackwardState[RIGHT] == backward)) { Motor_BackwardState[RIGHT] = none; }

	// check if backward-procedure has to be initialized
	if((Motor_TargetSpeed[LEFT] < 0) && (Motor_BackwardState[LEFT] == none)) { Motor_BackwardState[LEFT] = init; }
	if((Motor_TargetSpeed[RIGHT] < 0) && (Motor_BackwardState[RIGHT] == none)) { Motor_BackwardState[RIGHT] = init;	}

	if(((Motor_BackwardState[LEFT] == none) || (Motor_BackwardState[LEFT] == backward)) && ((Motor_BackwardState[RIGHT] == none) || (Motor_BackwardState[RIGHT] == backward)))
	{
		// Calculate/Update Control Parameters
		CCR_Value_Preset[LEFT]  = MOTOR_CCR_VALUE_OFFS + Motor_TargetSpeed[LEFT]  * MOTOR_CCR_VALUE_PRESET_GAIN;
		CCR_Value_Preset[RIGHT] = MOTOR_CCR_VALUE_OFFS + Motor_TargetSpeed[RIGHT] * MOTOR_CCR_VALUE_PRESET_GAIN;
		CCR_Value_P[LEFT]       = MOTOR_CONTROL_P * (Motor_TargetSpeed[LEFT]  - Encoder_Speed[LEFT]);
		CCR_Value_P[RIGHT]      = MOTOR_CONTROL_P * (Motor_TargetSpeed[RIGHT] - Encoder_Speed[RIGHT]);
		CCR_Value_I[LEFT]      += MOTOR_CONTROL_I * (Motor_TargetSpeed[LEFT]  - Encoder_Speed[LEFT]);
		CCR_Value_I[RIGHT]     += MOTOR_CONTROL_I * (Motor_TargetSpeed[RIGHT] - Encoder_Speed[RIGHT]);

		// Limit I Proportion
		CCR_Value_I[LEFT]  = CCR_Value_I[LEFT]  > MOTOR_CONTROL_I_MAX ? MOTOR_CONTROL_I_MAX : CCR_Value_I[LEFT];
		CCR_Value_I[RIGHT] = CCR_Value_I[RIGHT] > MOTOR_CONTROL_I_MAX ? MOTOR_CONTROL_I_MAX : CCR_Value_I[RIGHT];
		CCR_Value_I[LEFT]  = CCR_Value_I[LEFT]  < MOTOR_CONTROL_I_MIN ? MOTOR_CONTROL_I_MIN : CCR_Value_I[LEFT];
		CCR_Value_I[RIGHT] = CCR_Value_I[RIGHT] < MOTOR_CONTROL_I_MIN ? MOTOR_CONTROL_I_MIN : CCR_Value_I[RIGHT];

		// Reset I Propotion if target speed is 0
		CCR_Value_I[LEFT]  = Motor_TargetSpeed[LEFT]  == 0 ? 0 : CCR_Value_I[LEFT];
		CCR_Value_I[RIGHT] = Motor_TargetSpeed[RIGHT] == 0 ? 0 : CCR_Value_I[RIGHT];

		// Add up Proportions
		CCR_Value[LEFT]  = CCR_Value_Preset[LEFT]  + CCR_Value_P[LEFT]  + CCR_Value_I[LEFT];
		CCR_Value[RIGHT] = CCR_Value_Preset[RIGHT] + CCR_Value_P[RIGHT] + CCR_Value_I[RIGHT];

		// Limit total CCR-Value
		CCR_Value[LEFT]  = CCR_Value[LEFT]  > MOTOR_CCR_VALUE_MAX ? MOTOR_CCR_VALUE_MAX : CCR_Value[LEFT];
		CCR_Value[RIGHT] = CCR_Value[RIGHT] > MOTOR_CCR_VALUE_MAX ? MOTOR_CCR_VALUE_MAX : CCR_Value[RIGHT];
		CCR_Value[LEFT]  = CCR_Value[LEFT]  < MOTOR_CCR_VALUE_MIN ? MOTOR_CCR_VALUE_MIN : CCR_Value[LEFT];
		CCR_Value[RIGHT] = CCR_Value[RIGHT] < MOTOR_CCR_VALUE_MIN ? MOTOR_CCR_VALUE_MIN : CCR_Value[RIGHT];

		// Apply CCR-Value to PWM-Timer
		htim.Instance->CCR1 = CCR_Value[LEFT];
		htim.Instance->CCR2 = CCR_Value[RIGHT];
	}
	else
	{
		switch(Motor_BackwardState[LEFT])
		{
			case init:
			{
				// Initialize brake
				htim.Instance->CCR1 = MOTOR_CCR_VALUE_OFFS;
				if(CounterLeft >= 3)
				{
					Motor_BackwardState[LEFT] = braked;
					CounterLeft = 0;
				}
				else
				{
					CounterLeft++;
				}
				break;
			}

			case braked:
			{
				// Initialize forward
				htim.Instance->CCR1 = MOTOR_CCR_VALUE_OFFS + 500;
				if(CounterLeft >= 2)
				{
					Motor_BackwardState[LEFT] = forwarded;
					CounterLeft = 0;
				}
				else
				{
					CounterLeft++;
				}
				break;
			}

			case forwarded:
			{
				// Initialize zero
				htim.Instance->CCR1 = MOTOR_CCR_VALUE_OFFS;
				if(CounterLeft >= 4)
				{
					Motor_BackwardState[LEFT] = zeroed;
					CounterLeft = 0;
				}
				else
				{
					CounterLeft++;
				}
				break;
			}

			case zeroed:
			{
				// Try to move backward
				htim.Instance->CCR1 = MOTOR_CCR_VALUE_OFFS + Motor_TargetSpeed[LEFT]  * MOTOR_CCR_VALUE_PRESET_GAIN;
				if(CounterLeft >= 5)
				{
					if(Encoder_Speed[LEFT] < 0)
					{
						Motor_BackwardState[LEFT] = backward;
					}
					else
					{
						Motor_BackwardState[LEFT] = init;
					}
					CounterLeft = 0;
				}
				else
				{
					CounterLeft++;
				}
				break;
			}

			default:
			{
				CounterLeft = 0;
				break;
			}
		}

		switch(Motor_BackwardState[RIGHT])
		{
			case init:
			{
				// Initialize brake
				htim.Instance->CCR2 = MOTOR_CCR_VALUE_OFFS;
				if(CounterRight >= 3)
				{
					Motor_BackwardState[RIGHT] = braked;
					CounterRight = 0;
				}
				else
				{
					CounterRight++;
				}
				break;
			}

			case braked:
			{
				// Initialize forward
				htim.Instance->CCR2 = MOTOR_CCR_VALUE_OFFS + 500;
				if(CounterRight >= 2)
				{
					Motor_BackwardState[RIGHT] = forwarded;
					CounterRight = 0;
				}
				else
				{
					CounterRight++;
				}
				break;
			}

			case forwarded:
			{
				// Initialize zero
				htim.Instance->CCR2 = MOTOR_CCR_VALUE_OFFS;
				if(CounterRight >= 4)
				{
					Motor_BackwardState[RIGHT] = zeroed;
					CounterRight = 0;
				}
				else
				{
					CounterRight++;
				}
				break;
			}

			case zeroed:
			{
				// Try to move backward
				htim.Instance->CCR2 = MOTOR_CCR_VALUE_OFFS + Motor_TargetSpeed[RIGHT]  * MOTOR_CCR_VALUE_PRESET_GAIN;
				if(CounterRight >= 5)
				{
					if(Encoder_Speed[RIGHT] < 0)
					{
						Motor_BackwardState[RIGHT] = backward;
					}
					else
					{
						Motor_BackwardState[RIGHT] = init;
					}
					CounterRight = 0;
				}
				else
				{
					CounterRight++;
				}
				break;
			}

			default:
			{
				CounterRight = 0;
				break;
			}
		}
	}


}

/************************** GPIO Functions ************************/

void led_on(void)
{
	HAL_GPIO_WritePin(LED_GPIO, LED_PIN, GPIO_PIN_SET);
}

void led_off(void)
{
	HAL_GPIO_WritePin(LED_GPIO, LED_PIN, GPIO_PIN_RESET);
}

void buzzer_on(void)
{
	HAL_GPIO_WritePin(BUZZER_GPIO, BUZZER_PIN, GPIO_PIN_RESET);
}

void buzzer_off(void)
{
	HAL_GPIO_WritePin(BUZZER_GPIO, BUZZER_PIN, GPIO_PIN_SET);
}

bool imu_calibrationButton_pressed(void)
{

	return (HAL_GPIO_ReadPin(IMU_CALIBRATION_BUTTON_GPIO, IMU_CALIBRATION_BUTTON_PIN) == 0);
}

bool startButton_pressed(void)
{
	return (HAL_GPIO_ReadPin(START_BUTTON_GPIO, START_BUTTON_PIN) == 1);
}

bool startButton_raisingEdge(void)
{
	// local variables
	static bool beforeState = false;
	bool currentState;

	currentState = startButton_pressed();

	if((currentState == true) && (beforeState == false))
	{
		beforeState = currentState;
		return currentState;
	}

	beforeState = currentState;

	return false;
}


/************************ Callbacks Functions *********************/

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef* htim2)
{
	if(htim2->Channel == HAL_TIM_ACTIVE_CHANNEL_1)
	{
		// Encoder left
		++Encoder_Counter[LEFT];
		if(HAL_GPIO_ReadPin(ENCODER_L_SIGN_PORT, ENCODER_L_SIGN_PIN) == 0)
		{
			Encoder_Sign[LEFT] = -1; // -1: negative (counter-clockwise) direction of rotation
		}
		else
		{
			Encoder_Sign[LEFT] = 1;  // 1: positive (clockwise) direction of rotation
		}
	}

	if(htim2->Channel == HAL_TIM_ACTIVE_CHANNEL_2)
	{
		// Encoder right
		++Encoder_Counter[RIGHT];
		if(HAL_GPIO_ReadPin(ENCODER_R_SIGN_PORT, ENCODER_R_SIGN_PIN) == 0)
		{
			Encoder_Sign[RIGHT] = 1;  // 1: positive (clockwise) direction of rotation
		}
		else
		{
			Encoder_Sign[RIGHT] = -1; // -1: negative (counter-clockwise) direction of rotation
		}
	}
}
