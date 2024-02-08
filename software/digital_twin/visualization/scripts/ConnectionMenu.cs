using Godot;

public partial class ConnectionMenu : Control {
    private Global global;
    private Label connectionStatusLabel;

    public override void _Ready() {
        global = GetNode<Global>("/root/Global");
        global.userName = GetNode<LineEdit>("UserNameLabel/LineEdit");
        global.uri = GetNode<LineEdit>("UriLabel/LineEdit");
        global.password = GetNode<LineEdit>("PasswordLabel/LineEdit");
        global.port = GetNode<LineEdit>("PortLabel/LineEdit");
        connectionStatusLabel = GetNode<Label>("ConnectionStatusLabel");
    }

    private void OnConnectButtonPressed() {
        bool status = global.ConnectToRabbitMQ();
        if (status) {
            connectionStatusLabel.Text = "Connected";
        } else {
            connectionStatusLabel.Text = "Failed to connect";
        }
    }

    private void OnStartButtonPressed() {
        GetTree().ChangeSceneToFile("res://scenes/incubator.tscn");
    }
}
