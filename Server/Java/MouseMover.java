import java.awt.AWTException;
import java.awt.MouseInfo;
import java.awt.Point;
import java.awt.Robot;
import java.awt.event.InputEvent;

public class MouseMover {
    static int directionX = 0;
    static int directionY = 0;
    static double speed = 5.833;
    static int isThreadStarted = 0;
    static float lastAccX = 0.0f;
    static float lastAccY = 0.0f;
    static float lastAccZ = 0.0f;

    public static void ReceiveData(String data) throws AWTException{
        Robot robot = new Robot();
            System.out.println(data);

        if (data.equals("StopServer")){
            Runtime.getRuntime().halt(0);
        }else if (data.startsWith("Scroll: ")){
        if (data.equals("Scroll: UP")){
            robot.mouseWheel(-(int)(speed / (speed - (speed * 0.2))));
        }else if (data.equals("Scroll: DOWN")){
            robot.mouseWheel((int)(speed / (speed - (speed * 0.2))));
        }
        }else if (data.startsWith("Latency(")){
            long latencyValue = Long.parseLong(data.replace("Latency(", "").replace(")", ""));

            System.out.println("Latency: " + latencyValue + "ms");
        }else if (data.startsWith("\"Tpad(")){
                    Point p = MouseInfo.getPointerInfo().getLocation();
                    int mouseX = (int)p.getX();
                    int mouseY = (int)p.getY();

                    String inside = data.substring(data.indexOf("(") + 1, data.indexOf(")"));

                    String[] parts = inside.split(",");

                    int xValue = ((int)Double.parseDouble(parts[0].trim()) * (int)speed / 2) + mouseX;
                    int yValue = ((int)Double.parseDouble(parts[1].trim()) * (int)speed / 2) + mouseY;

                    robot.mouseMove(xValue, yValue);
        }else if (data.equals("RCD") || data.equals("RCU") || data.equals("LCD") || data.equals("LCU") || data.equals("BD") || data.equals("BU") || data.equals("FD") || data.equals("FU") || data.equals("WCD") || data.equals("WCU")){
            if (data.equals("RCD")){
                try {
                    robot.mousePress(InputEvent.BUTTON3_DOWN_MASK);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }else if (data.equals("RCU")){
                 try {
                    robot.mouseRelease(InputEvent.BUTTON3_DOWN_MASK);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }else if (data.equals("LCU")) {
                 try {
                    robot.mouseRelease(InputEvent.BUTTON1_DOWN_MASK);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }else if (data.equals("LCD")){
                 try {
                    robot.mousePress(InputEvent.BUTTON1_DOWN_MASK);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }else if (data.equals("BD")){
                try {
                    robot.mousePress(InputEvent.getMaskForButton(4));
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }else if (data.equals("BU")){
                 try {
                    robot.mouseRelease(InputEvent.getMaskForButton(4));
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }else if (data.equals("FD")) {
                 try {
                    robot.mousePress(InputEvent.getMaskForButton(5));
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }else if (data.equals("FU")){
                 try {
                    robot.mouseRelease(InputEvent.getMaskForButton(5));
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }else if (data.equals("WCD")){
                 try {
                    robot.mousePress(InputEvent.BUTTON2_DOWN_MASK);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }else if (data.equals("WCU")){
                 try {
                    robot.mouseRelease(InputEvent.BUTTON2_DOWN_MASK);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }else if (data.startsWith("MouseSpeed: ")) {
                String onlySpeedValue = data.replace("MouseSpeed: ", "");
                Double mouseSpeed = Double.parseDouble(onlySpeedValue);
                speed = mouseSpeed / 6;
        }else if (data.startsWith("\"{'accX':")){
        // Getting accX value
        int jsonStartX = data.indexOf("accX") + 7;
        int jsonEndX = data.indexOf(",", jsonStartX);
        String xStarting = data.substring(jsonStartX, jsonEndX).trim();
        double accX = Double.parseDouble(xStarting);
        //System.out.println(accX);

        /*
        // Getting accY value
        int jsonStartY = data.indexOf("accY") + 7;
        int jsonEndY = data.indexOf(",", jsonStartY);
        String yStarting = data.substring(jsonStartY, jsonEndY).trim();
        double accY = Double.parseDouble(yStarting);
        //System.out.println(accY);
        */

        // Getting accY value
        int jsonStartY = data.indexOf("accY") + 7;
        int jsonEndY = data.indexOf("}", jsonStartY);
        String yStarting = data.substring(jsonStartY, jsonEndY).trim();
        double accY = Double.parseDouble(yStarting);
        //System.out.println(accY);

        /*
        // Getting accZ value
        int jsonStartZ = data.indexOf("accZ") + 7;
        int jsonEndZ = data.indexOf("}", jsonStartZ);
        String zStarting = data.substring(jsonStartZ, jsonEndZ).trim();
        double accZ = Double.parseDouble(zStarting);
        //System.out.println(accZ);
        */

        accX = (float) accX;
        accY = (float) accY;
        // accZ = (float) accZ;

        lastAccX = (float) accX;
        lastAccY = (float) accY;
        // lastAccZ = (float) accZ;

        if (accX > 1){
            System.out.println("Left: " + accX);
            directionX = -1;
        }else if (accX < -1){
            System.err.println("Right: " + accX);
            directionX = 1;
        }else{
            Thread sleepThread200X = new Thread(() -> {
            try {
                Thread.sleep(200);
                if (!(lastAccX > 0.5) && !(lastAccX < -0.5)){
                    directionX = 0;
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
            });
            sleepThread200X.start();
        }

        if (accY > 0.5){
            System.out.println("Down: " + accY);
            directionY = 1;
        }else if (accY < -0.5){
            System.err.println("Up: " + accY);
            directionY = -1;
        }else{
            Thread sleepThread200Y = new Thread(() -> {
            try {
                Thread.sleep(200);
                if (!(lastAccY > 0.5) && !(lastAccY < -0.5)){
                    directionY = 0;
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
            });
            sleepThread200Y.start();
        }

        Thread mouseMoveThread = new Thread(() -> {
            try {
                  while (true){
                    Point p = MouseInfo.getPointerInfo().getLocation();
                    int mouseX = (int)p.getX();
                    int mouseY = (int)p.getY();

                    mouseX += directionX * speed;
                    mouseY += directionY * speed;

                    robot.mouseMove(mouseX, mouseY);
                    Thread.sleep(10);
                }
            } catch (InterruptedException e){
                e.printStackTrace();
            }
        });

        if (isThreadStarted == 0){
            mouseMoveThread.start();
            isThreadStarted = 1;
        }
        }

    }
}