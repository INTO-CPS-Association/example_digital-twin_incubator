using Godot;

public partial class ConnectionMenu : Control {
    private Global global;
    private Label connectionStatusLabel;
    private Label startLabel;
    private bool connectionStatus = false;

    public override void _Ready() {
        global = GetNode<Global>("/root/Global");
        global.userName = GetNode<LineEdit>("UserNameLabel/LineEdit");
        global.hostName = GetNode<LineEdit>("HostNameLabel/LineEdit");
        global.password = GetNode<LineEdit>("PasswordLabel/LineEdit");
        global.port = GetNode<LineEdit>("PortLabel/LineEdit");
        connectionStatusLabel = GetNode<Label>("ConnectionStatusLabel");
        startLabel = GetNode<Label>("StartLabel");
    }

    private void OnConnectButtonPressed() {      
        try {
            connectionStatus = global.ConnectToRabbitMQ();
            connectionStatusLabel.Text = "Connected";
            startLabel.Text = "";
        }
        catch (System.Exception) {
            connectionStatusLabel.Text = "Failed to connect";
        }
    }

    private void OnStartButtonPressed() {
        if (connectionStatus) {
            global.GetTree().ChangeSceneToFile("res://scenes/incubator.tscn");
        } else {
            startLabel.Text = "Connect to RabbitMQ first";
        }
    }
}
