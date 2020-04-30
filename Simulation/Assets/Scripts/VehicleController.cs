using UnityEngine;

namespace Assets.Scripts
{
    public class VehicleController : MonoBehaviour
    {
        void LateUpdate()
        {
            if (Input.GetKey("w"))
                transform.Translate(Vector3.forward * 50 * Time.deltaTime, Space.Self);

            if (Input.GetKey("a"))
                transform.Rotate(Vector3.up * -50 * Time.deltaTime, Space.Self);

            if (Input.GetKey("s"))
                transform.Translate(Vector3.back * 30 * Time.deltaTime, Space.Self);

            if (Input.GetKey("d"))
                transform.Rotate(Vector3.up * 50 * Time.deltaTime, Space.Self);
        }
    }
}
