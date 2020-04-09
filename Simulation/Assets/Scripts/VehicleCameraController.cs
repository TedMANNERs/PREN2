using System;
using System.IO;
using System.IO.Pipes;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace Assets.Scripts
{
    public class VehicleCameraController : MonoBehaviour
    {
        private Camera _camera;
        private TcpClient _tcpClient;
        private BinaryWriter _writer;
        private NetworkStream _networkStream;

        // Start is called before the first frame update
        void Start()
        {
            _tcpClient = new TcpClient("localhost", 6048);
            _networkStream = _tcpClient.GetStream();
            _writer = new BinaryWriter(_networkStream);
            _camera = GetComponent<Camera>();
            InvokeRepeating(nameof(SendCameraFrame), 3f, 0.3f);
        }

        // Update is called once per frame
        void Update()
        {
        }

        void OnDestroy()
        {
            _writer.Close();
            _networkStream.Close();
            _tcpClient.Close();
        }

        private void SendCameraFrame()
        {
            if (_tcpClient.Client.Connected && _writer != null)
            {
                RenderTexture rt = new RenderTexture(1920, 1080, 24);
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
                _writer.Write(bytes.Length);
                _writer.Write(bytes);
                _writer.Flush();
            }
        }
    }
}
