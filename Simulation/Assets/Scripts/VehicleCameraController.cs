using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.IO.Pipes;
using System.Linq;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace Assets.Scripts
{
    public class VehicleCameraController : MonoBehaviour
    {
        private Camera _camera;
        private Task _tcpTask;
        private readonly CancellationTokenSource _tokenSource = new CancellationTokenSource();
        private CancellationToken _cancellationToken;
        private readonly ConcurrentQueue<byte[]> _imageQueue = new ConcurrentQueue<byte[]>();

        // Start is called before the first frame update
        void Start()
        {
            _cancellationToken = _tokenSource.Token;
            _tcpTask = Task.Run(KeepConnected, _cancellationToken);
            _camera = GetComponent<Camera>();
            InvokeRepeating(nameof(EnqueueCameraFrame), 3f, 0.1f);
        }

        private void KeepConnected()
        {
            TcpClient tcpClient = null;
            BinaryWriter writer = null;
            while (!_cancellationToken.IsCancellationRequested)
            {
                if (tcpClient == null || !tcpClient.Client.Connected)
                {
                    try
                    {
                        tcpClient = new TcpClient("127.0.0.1", 5000) {SendTimeout = 30000};
                        var stream = tcpClient.GetStream();
                        writer = new BinaryWriter(stream);
                    }
                    catch (Exception e)
                    {
                        Debug.Log(e);
                    }
                }
                else
                {
                    if (_imageQueue.Any())
                    {
                        if (_imageQueue.TryDequeue(out byte[] bytes))
                        {
                            try
                            {
                                writer.Write(bytes.Length);
                                writer.Write(bytes);
                                writer.Flush();
                            }
                            catch (Exception e)
                            {
                                Debug.Log(e);
                            }
                        }
                    }
                }

                Thread.Sleep(80);
            }

            writer.Close();
            writer.Dispose();
            tcpClient.Close();
            tcpClient.Dispose();
        }

        void OnDestroy()
        {
            _tokenSource.Cancel();
        }

        private void EnqueueCameraFrame()
        {
            RenderTexture rt = new RenderTexture(416, 416, 24);
            _camera.targetTexture = rt;

            _camera.Render();
            Texture2D image = new Texture2D(_camera.targetTexture.width, _camera.targetTexture.height);
            RenderTexture.active = rt;
            image.ReadPixels(new Rect(0, 0, _camera.targetTexture.width, _camera.targetTexture.height), 0, 0);
            _camera.targetTexture = null;
            RenderTexture.active = null; // JC: added to avoid errors
            Destroy(rt);


            byte[] bytes = image.EncodeToPNG();
            Destroy(image);
            
            _imageQueue.Enqueue(bytes);
        }
    }
}
