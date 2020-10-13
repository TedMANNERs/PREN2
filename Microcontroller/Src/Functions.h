/*
 * Functioncs.h
 *
 *  Created on: 01.03.2020
 *      Author: T.Burkard
 */

#ifndef FUNCTIONS_H_
#define FUNCTIONS_H_

/******************************************************************/
/**************************** Includes ****************************/
/******************************************************************/

#include <stdint.h>
#include "stm32f4xx_hal.h"
#include "usb_device.h"
#include "usbd_cdc_if.h"
#include "stdbool.h"


/******************************************************************/
/***************************** Defines ****************************/
/******************************************************************/

#define CONVERT_TO_MILLI_G (1000 * 3.3 / 255 / 0.3) // 1000: because we want milli g
													// 3.3 V: Vref of ADC
													// 255: Resolution of ADC
													// 0.3 g/V (sensor specification)

#define DISTANCE_PER_STEP (0.5)						// Distance the wheel drives per Encoder-Step in [mm]
                                                    // 2*Pi*80mm / (512*3) = 0.491 mm
                                                    // 512: encoder pulses per full encoder rotation, 3: gear ratio between encoder and wheel, 80mm: wheel radius
#define COUNTER_FREQUENCY (4500000)					// 72 MHz / 16 (Prescale) = 4.5 MHz

#define IMU_ADCVALUE_0g		116  // expected ADC-Value at 0g (acc. datasheet)
#define IMU_ADCVALUE_1g		139  // expected ADC-Value at 1g (acc. datasheet)

#define ADC_CH_AMOUNT		5

// Indexes
#define LEFT  0
#define RIGHT 1

#define X_AXIS 0
#define Y_AXIS 1
#define Z_AXIS 2


// Encoder
#define ENCODER_L_SIGN_PORT GPIOB
#define ENCODER_L_SIGN_PIN	GPIO_PIN_0
#define ENCODER_R_SIGN_PORT	GPIOB
#define ENCODER_R_SIGN_PIN	GPIO_PIN_5
#define ENCODER_MEASUREMENT_TIME 100000  // in [us]

// Buzzer
#define BUZZER_GPIO GPIOB
#define BUZZER_PIN	GPIO_PIN_10

// LED
#define LED_GPIO 	GPIOA
#define LED_PIN	 	GPIO_PIN_5

// IMU Calibration Button
#define IMU_CALIBRATION_BUTTON_GPIO GPIOC
#define IMU_CALIBRATION_BUTTON_PIN  GPIO_PIN_13

// Start Button
#define START_BUTTON_GPIO GPIOA
#define START_BUTTON_PIN  GPIO_PIN_9

// USB Commands
#define USB_CMD_START			0x01
#define USB_CMD_TARGETVECTOR	0x02
#define USB_CMD_SENSORDATA		0x03
#define USB_CMD_PLAYAUDIO		0x04
#define USB_CMD_STOP			0x05
#define USB_CMD_LED				0xF0

#define USB_CMD_PLAYAUDIO_SHORTBEEP	0x01
#define USB_CMD_PLAYAUDIO_LONGBEEP	0x02

#define BUZZER_SHORTBEEP_DURATION	10    // Duration in [10 ms]
#define BUZZER_LONGBEEP_DURATION   100    // Duration in [10 ms]

// USB Commands Datasize (w/o Cmd-Byte) in Byte
#define USB_CMD_DATASIZE_START			0
#define USB_CMD_DATASIZE_TARGETVECTOR 	4
#define USB_CMD_DATASIZE_SENSORDATA	   14
#define USB_CMD_DATASIZE_PLAYAUDIO		1
#define USB_CMD_DATASIZE_STOP			0
#define USB_CMD_DATASIZE_LED			1

#define USB_SENDBUFFER_DATASIZE_MAX	   14

// Motor Control
#define MOTOR_CCR_VALUE_OFFS         6126   // If timer CCR-Register is set to this value, motor does not turn
#define MOTOR_CCR_VALUE_PRESET_GAIN  0.20   // Multiplied by the Motor_TargetSpeed and added to MOTOR_CCR_VALUE_OFFS, this is the preset CCR value (= expected CCR value for required speed)
#define MOTOR_CCR_VALUE_MAX          8400   // Max allowed CCR Value for Motor Control
#define MOTOR_CCR_VALUE_MIN          3900   // Min allowed CCR Value for Motor Control

#define MOTOR_CONTROL_P       0.15          // Control P: 0.15 CCR per mm/s difference
#define MOTOR_CONTROL_I       0.06          // Control P: 0.06 CCR per mm/s difference, each 100ms
#define MOTOR_CONTROL_I_MAX   1000          // Max I Proportion of Motor control
#define MOTOR_CONTROL_I_MIN  -1000          // Min I Proportion of Motor control

#define MOTOR_ANGLE_MAX       90            // Max Angle in Degrees
#define MOTOR_ANGLE_MIN      -90            // Min Angle in Degrees

#define MOTOR_SPEED_MAX       5000          // Max Speed in mm/s
#define MOTOR_SPEED_MIN      -5000          // Min Speed in mm/s

typedef enum
{
	none,
	init,
	braked,
	forwarded,
	zeroed,
	backward
}t_motor_backwardState;

/******************************************************************/
/*********************** Function-Declarations ********************/
/******************************************************************/

/************************** Init Functions ************************/
void TIM_Init(TIM_HandleTypeDef htim2, TIM_HandleTypeDef htim3);

/************************* Sensor Functions ***********************/
void IMU_calibrate_offset(int8_t* IMU_OffsetCalibration, const uint8_t* ADCbuffer);
void Encoder_calculateDeltaValue(uint32_t* Encoder_DeltaValue);
void Encoder_calculateSpeed(int16_t* Encoder_Speed);
uint16_t DistanceSensor_convert(uint8_t ADC_DistanceValue);

/************** USB prepair SensorDataBuff Functions **************/
void USB_prepair_SensorDataBuffer_IMU(uint8_t* USBsendBuffer, const uint8_t* ADCbuffer, const int8_t* IMU_OffsetCalibration);
void USB_prepair_SensorDataBuffer_Encoder(uint8_t* SensorDataBuffer, const int16_t* Encoder_Speed);
void USB_prepair_SensorDataBuffer_DistanceSensor(uint8_t* USBsendBuffer, const uint8_t* ADCbuffer);

/*********************** USB send Functions ***********************/
void USB_send_start(void);
void USB_send_stop(void);
void USB_send_sensordata(const uint8_t* ADCbuffer, const int8_t* IMU_OffsetCalibration, const int16_t* Encoder_Speed);
void USB_send_Command(uint8_t Cmd, uint8_t* dataBuffer, uint8_t dataSize);

/********************* USB receive Function ***********************/
void USB_receive_handle(int16_t* Motor_TargetSpeed, uint16_t MainCounter, bool* Buzzer_ActiveFlag, uint16_t* Buzzer_ResetCounter, bool* JetsonReady);

/********************** Buzzer Functions **************************/
void buzzer_initiate_longbeep(bool* Buzzer_ActiveFlag, uint16_t MainCounter, uint16_t* Buzzer_ResetCounter);
void buzzer_initiate_shortbeep(bool* Buzzer_ActiveFlag, uint16_t MainCounter, uint16_t* Buzzer_ResetCounter);

/************************ Motor Control ***************************/
void Motor_Control(TIM_HandleTypeDef htim,const int16_t* Encoder_Speed,const int16_t* Motor_TargetSpeed);
void adjust_TargetSpeed(int16_t* Motor_TargetSpeed, int16_t* Motor_TargetSpeedReceived);

/************************** GPIO Functions ************************/
void led_on(void);
void led_off(void);
void buzzer_on(void);
void buzzer_off(void);
bool imu_calibrationButton_pressed(void);
bool startButton_pressed(void);
bool startButton_raisingEdge(void);

#endif /* FUNCTIONS_H_ */
