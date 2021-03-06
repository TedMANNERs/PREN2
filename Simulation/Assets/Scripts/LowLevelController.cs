﻿using System;
using System.Collections;
using System.IO.Ports;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace Assets.Scripts
{
    internal enum CommandType : byte
    {
        Start = 0x01,
        SendTargetVector = 0x02,
        SendSensorData = 0x03,
        PlayAudio = 0x04,
        Stop = 0x0,
        Led = 0xF0
    }

    internal enum AudioCommand : byte
    {
        ShortBeep = 0x01,
        LongBeep = 0x02
    }

    internal enum LEDCommand : byte
    { 
        Off = 0x00,
        On = 0x01
    }

    internal class TargetVector
    {
        public TargetVector(short speed, short angle)
        {
            Speed = speed;
            Angle = angle;
        }

        public short Speed { get; set; }
        public short Angle { get; set; }
    }

    public class LowLevelController : MonoBehaviour
    {
        private SerialPort _serialPort;
        private Task _listenerTask;
        private readonly CancellationTokenSource _listenerTokenSource = new CancellationTokenSource();
        private CancellationToken _cancellationToken;
        private TargetVector _targetVector;
        private Rigidbody _rb;
        private WheelController _wheelController;

        private bool _isVehicleReady;

        [SerializeField]
        private bool _isControlledByPlayer;

        [SerializeField]
        private int _turnFactor = 20;

        // Start is called before the first frame update
        void Start()
        {
            _rb = GetComponent<Rigidbody>();
            _wheelController = GetComponent<WheelController>();

            _serialPort = new SerialPort("COM4", 115200, Parity.Odd,8, StopBits.One);
            _cancellationToken = _listenerTokenSource.Token;
            _listenerTask = Task.Run(Listen, _cancellationToken);
            _serialPort.WriteTimeout = 100;
            _serialPort.Open();
            byte[] startBuffer = {(byte) CommandType.Start};
            _serialPort.Write(startBuffer, 0, startBuffer.Length);
            Invoke(nameof(ReleaseVehicle), 3f);
            InvokeRepeating(nameof(SendSensorData),3f, 0.1f);
        }

        // FixedUpdate is called every fixed frame-rate frame
        void FixedUpdate()
        {
            if (_isControlledByPlayer || _targetVector == null)
                return;
            if (!_isVehicleReady)
                return;

            TargetVectorReceived(_targetVector.Speed, _targetVector.Angle);
            _targetVector = null;
        }

        void OnDestroy()
        {
            try
            {
                byte[] stopBuffer = {(byte) CommandType.Stop};
                _serialPort.Write(stopBuffer, 0, stopBuffer.Length);
            }
            catch (Exception e)
            {
                Debug.Log(e);
            }
            finally
            {
                _listenerTokenSource.Cancel();
                _serialPort.Close();
            }
        }

        void ReleaseVehicle()
        {
            _isVehicleReady = true;
        }

        private void Listen()
        {
            while (!_cancellationToken.IsCancellationRequested)
            {
                if (_serialPort.IsOpen)
                {
                    try
                    {
                        int data = _serialPort.ReadByte();
                        CommandType commandType = (CommandType)data;
                        switch (commandType)
                        {
                            case CommandType.SendTargetVector:
                                byte[] buffer = new byte[4]; // 4 = 2 x 2 signed int 16
                                _serialPort.Read(buffer, 0, 4);

                                if (BitConverter.IsLittleEndian)
                                {
                                    Array.Reverse(buffer, 0, 2);
                                    Array.Reverse(buffer, 2, 2);
                                }

                                short speed = BitConverter.ToInt16(buffer, 0);
                                short angle = BitConverter.ToInt16(buffer, 2);
                                _targetVector = new TargetVector(speed, angle);
                                break;
                            case CommandType.PlayAudio:
                                AudioCommand audioCommand = (AudioCommand)_serialPort.ReadByte();
                                Debug.Log($"Received AudioCommand = {audioCommand}");
                                break;
                            case CommandType.Start:
                                Debug.Log("Received Start");
                                break;
                            case CommandType.Stop:
                                Debug.Log("Received Stop");
                                break;
                            case CommandType.Led:
                                LEDCommand ledCommand = (LEDCommand)_serialPort.ReadByte();
                                Debug.Log($"Received LEDCommand = {ledCommand}");
                                break;
                            default:
                                throw new ArgumentOutOfRangeException();
                        }
                    }
                    catch (Exception exception)
                    {
                        Console.WriteLine(exception);
                        Debug.Log(exception);
                    }
                }
            }
        }

        private void SendSensorData()
        {
            //TODO: Send sensor data
        }

        private void TargetVectorReceived(short speed, short angle)
        {
            Debug.Log($"Received TargetVector: Speed = {speed}, angle = {angle}");
            if (angle < 0)
                _wheelController.Apply(speed + angle * _turnFactor, speed); //Left
            else if (angle > 0)
                _wheelController.Apply(speed, speed - angle * _turnFactor); //Right
            else
            {
                if (speed < 0)
                    _wheelController.Apply(speed, speed); //Reverse
                else
                    _wheelController.Apply(speed, speed); // Forward
            }
        }
    }
}
