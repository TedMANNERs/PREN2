using UnityEngine;

public class WheelController : MonoBehaviour
{
    private HingeJoint _joint;
    [SerializeField]
    private int _targetVelocity = 100;

    [SerializeField]
    private int _force = 100;

    [SerializeField]
    private KeyCode _key = KeyCode.UpArrow;

    // Start is called before the first frame update
    void Start()
    {
        _joint = GetComponent<HingeJoint>();
        _joint.useMotor = true;
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKey(_key))
        {
            var jointMotor = _joint.motor;
            jointMotor.targetVelocity = _targetVelocity;
            jointMotor.force = _force;
            _joint.motor = jointMotor;
        }
        else
        {
            _joint.motor = new JointMotor();
        }
    }
}
