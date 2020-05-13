using System;
using UnityEngine;

namespace Assets.Scripts
{
    public class InertialMeasurementUnit : MonoBehaviour
    {
        float updateFreq = 1.0f;
        Vector3 angularVelocity;
        Vector3 angularAcceleration;
        Vector3 linearVelocity;
        Vector3 linearAcceleration;
        private Vector3 lastPosition;
        private Vector3 lastAngle;
        private Vector3 lastLinearVelocity;
        private Vector3 lastAngularVelocity;
        private float timer = 0.0f;

        [SerializeField]
        private LowLevelController _lowLevelController;

        // Start is called before the first frame update
        void Start()
        {
        
        }

        // Update is called once per frame
        void Update()
        {
            timer += Time.deltaTime;
            if (timer > (1 / updateFreq))
            {

                lastLinearVelocity = linearVelocity;
                lastAngularVelocity = angularVelocity;

                var lastPosInv = transform.InverseTransformPoint(lastPosition);

                linearVelocity.x = (0 - lastPosInv.x) / timer;
                linearVelocity.y = (0 - lastPosInv.y) / timer;
                linearVelocity.z = (0 - lastPosInv.z) / timer;

                var deltaX = Mathf.Abs((transform.rotation.eulerAngles).x) - lastAngle.x;
                if (Mathf.Abs(deltaX) < 180 && deltaX > -180) angularVelocity.x = deltaX / timer;
                else
                {
                    if (deltaX > 180) angularVelocity.x = (360 - deltaX) / timer;
                    else angularVelocity.x = (360 + deltaX) / timer;
                }

                var deltaY = Mathf.Abs((transform.rotation.eulerAngles).y) - lastAngle.y;
                if (Mathf.Abs(deltaY) < 180 && deltaY > -180) angularVelocity.y = deltaY / timer;
                else
                {
                    if (deltaY > 180) angularVelocity.y = (360 - deltaY) / timer;
                    else angularVelocity.y = (360 - deltaY) / timer;
                }

                var deltaZ = Mathf.Abs((transform.rotation.eulerAngles).z) - lastAngle.z;
                if (Mathf.Abs(deltaZ) < 180 && deltaZ > -180) angularVelocity.z = deltaZ / timer;
                else
                {
                    if (deltaZ > 180) angularVelocity.z = (360 - deltaZ) / timer;
                    else angularVelocity.z = (360 + deltaZ) / timer;
                }


                linearAcceleration.x = (linearVelocity.x - lastLinearVelocity.x) / timer;
                linearAcceleration.y = (linearVelocity.y - lastLinearVelocity.y) / timer;
                linearAcceleration.z = (linearVelocity.z - lastLinearVelocity.z) / timer;
                angularAcceleration.x = ((angularVelocity.x - lastAngularVelocity.x) / timer) / 9.81f;
                angularAcceleration.y = ((angularVelocity.y - lastAngularVelocity.y) / timer) / 9.81f;
                angularAcceleration.z = ((angularVelocity.z - lastAngularVelocity.z) / timer) / 9.81f;

                lastPosition = transform.position;

                lastAngle.x = Mathf.Abs((transform.rotation.eulerAngles).x);
                lastAngle.y = Mathf.Abs((transform.rotation.eulerAngles).y);
                lastAngle.z = Mathf.Abs((transform.rotation.eulerAngles).z);

                timer = 0;
                //Debug.Log($"X={linearAcceleration.x}, Y={linearAcceleration.y}, Z={linearAcceleration.z}, ");
            }
        }
    }
}
