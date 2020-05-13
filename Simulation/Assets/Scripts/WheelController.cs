using UnityEngine;

public class WheelController : MonoBehaviour
{
    [SerializeField]
    private HingeJoint _wheelLeftFront;
    [SerializeField]
    private HingeJoint _wheelLeftBack;
    [SerializeField]
    private HingeJoint _wheelRightFront;
    [SerializeField]
    private HingeJoint _wheelRightBack;

    [SerializeField]
    private int _targetVelocityStraight = 300;
    [SerializeField]
    private int _targetVelocityTurn = 400;

    [SerializeField]
    private int _force = 100;

    public float WheelLeftFrontVelocity =>  _wheelLeftFront.velocity;
    public float WheelLeftBackVelocity =>  _wheelLeftBack.velocity;
    public float WheelRightFrontVelocity =>  _wheelRightFront.velocity;
    public float WheelRightBackVelocity =>  _wheelRightBack.velocity;

    // Start is called before the first frame update
    void Start()
    {
        _wheelLeftFront.useMotor = true;
        _wheelLeftBack.useMotor = true;
        _wheelRightFront.useMotor = true;
        _wheelRightBack.useMotor = true;
    }

    // Update is called once per frame
    void Update()
    {
        bool pressedA = Input.GetKey(KeyCode.A);
        bool pressedD = Input.GetKey(KeyCode.D);
        bool pressedS = Input.GetKey(KeyCode.S);

        if (pressedA && !pressedD)
            TurnLeft();
        else if (!pressedA && pressedD)
            TurnRight();
        else if (pressedA)
            MoveForward();
        else
            Neutral();

        if (pressedS)
            Reverse();
    }

    public void Reverse()
    {
        _wheelLeftFront.motor = UpdateMotor(-150, _force);
        _wheelLeftBack.motor = UpdateMotor(-150, _force);
        _wheelRightFront.motor = UpdateMotor(150, _force);
        _wheelRightBack.motor = UpdateMotor(150, _force);
    }

    public void Neutral()
    {
        _wheelLeftFront.motor = new JointMotor();
        _wheelLeftBack.motor = new JointMotor();
        _wheelRightFront.motor = new JointMotor();
        _wheelRightBack.motor = new JointMotor();
    }

    public void MoveForward()
    {
        _wheelLeftFront.motor = UpdateMotor(_targetVelocityStraight, _force);
        _wheelLeftBack.motor = UpdateMotor(_targetVelocityStraight, _force);
        _wheelRightFront.motor = UpdateMotor(_targetVelocityStraight * -1, _force);
        _wheelRightBack.motor = UpdateMotor(_targetVelocityStraight * -1, _force);
    }

    public void TurnLeft()
    {
        _wheelLeftFront.motor = UpdateMotor(1, _force);
        _wheelLeftBack.motor = UpdateMotor(1, _force);
        _wheelRightFront.motor = UpdateMotor(_targetVelocityTurn * -1, _force);
        _wheelRightBack.motor = UpdateMotor(_targetVelocityTurn * -1, _force);
    }

    public void TurnRight()
    {
        _wheelLeftFront.motor = UpdateMotor(_targetVelocityTurn, _force);
        _wheelLeftBack.motor = UpdateMotor(_targetVelocityTurn, _force);
        _wheelRightFront.motor = UpdateMotor(-1, _force);
        _wheelRightBack.motor = UpdateMotor(-1, _force);
    }

    private JointMotor UpdateMotor(int targetVelocity, int force)
    {
        JointMotor jointMotor = _wheelLeftFront.motor;
        jointMotor.targetVelocity = targetVelocity;
        jointMotor.force = force;
        return jointMotor;
    }
}
