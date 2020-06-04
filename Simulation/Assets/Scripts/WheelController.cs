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

    [SerializeField]
    private int _targetVelocityTurnOpposite = 1;

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
            TurnLeft(_targetVelocityTurn);
        else if (!pressedA && pressedD)
            TurnRight(_targetVelocityTurn);
        else if (pressedA)
            MoveForward(_targetVelocityStraight);
        else
            Neutral();

        if (pressedS)
            Reverse(150);
    }

    public void Reverse(int targetVelocity)
    {
        _wheelLeftFront.motor = UpdateMotor(0-targetVelocity, _force);
        _wheelLeftBack.motor = UpdateMotor(0-targetVelocity, _force);
        _wheelRightFront.motor = UpdateMotor(targetVelocity, _force);
        _wheelRightBack.motor = UpdateMotor(targetVelocity, _force);
    }

    public void Neutral()
    {
        _wheelLeftFront.motor = new JointMotor();
        _wheelLeftBack.motor = new JointMotor();
        _wheelRightFront.motor = new JointMotor();
        _wheelRightBack.motor = new JointMotor();
    }

    public void MoveForward(int targetVelocity)
    {
        _wheelLeftFront.motor = UpdateMotor(targetVelocity, _force);
        _wheelLeftBack.motor = UpdateMotor(targetVelocity, _force);
        _wheelRightFront.motor = UpdateMotor(targetVelocity * -1, _force);
        _wheelRightBack.motor = UpdateMotor(targetVelocity * -1, _force);
    }

    public void TurnLeft(int targetVelocity)
    {
        _wheelLeftFront.motor = UpdateMotor(_targetVelocityTurnOpposite, _force);
        _wheelLeftBack.motor = UpdateMotor(_targetVelocityTurnOpposite, _force);
        _wheelRightFront.motor = UpdateMotor(targetVelocity * -1, _force);
        _wheelRightBack.motor = UpdateMotor(targetVelocity * -1, _force);
    }

    public void TurnRight(int targetVelocity)
    {
        _wheelLeftFront.motor = UpdateMotor(targetVelocity, _force);
        _wheelLeftBack.motor = UpdateMotor(targetVelocity, _force);
        _wheelRightFront.motor = UpdateMotor(-_targetVelocityTurnOpposite, _force);
        _wheelRightBack.motor = UpdateMotor(-_targetVelocityTurnOpposite, _force);
    }

    private JointMotor UpdateMotor(int targetVelocity, int force)
    {
        return new JointMotor { targetVelocity = targetVelocity, force = force }; ;
    }

    public void Apply(int leftVelocity, int rightVelocity)
    {
        _wheelLeftFront.motor = UpdateMotor(leftVelocity, _force);
        _wheelLeftBack.motor = UpdateMotor(leftVelocity, _force);
        _wheelRightFront.motor = UpdateMotor(-rightVelocity, _force);
        _wheelRightBack.motor = UpdateMotor(-rightVelocity, _force);
    }
}
