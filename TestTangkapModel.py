from SpoutGL import SpoutReceiver

receiver = SpoutReceiver()

print("Create OpenGL:", receiver.createOpenGL())
print("GL Ready:", receiver.isGLDXReady())

receiver.setReceiverName("VTubeStudioSpout")

print("Senders:", receiver.getSenderList())
print("Connected:", receiver.isConnected())

try:
    ok = receiver.receiveImage(None, 0, False, 0)
    print("receiveImage:", ok)
except Exception as e:
    print("Error:", e)

print("Connected after receive:", receiver.isConnected()) 