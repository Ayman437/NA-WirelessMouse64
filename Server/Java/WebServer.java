import com.sun.net.httpserver.*;
import java.io.*;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.KeyStore;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import javax.net.ssl.*;

// Run this only from ../ path!

public class WebServer {
    static String SSLCertificateKeyStorePath = "";
    static String WebApplicationPath = "";
    static String Key = "";
    static String ConfigurationFilePath = System.getProperty("user.dir").replace('\\', '/') + "/Server/Configuration.json";
    static String LastVisitsLogPath = System.getProperty("user.dir").replace('\\', '/') + "/Server/Info/LastVisitsLog.txt";
    static String ServerOutputsPath = System.getProperty("user.dir").replace('\\', '/') + "/Server/Info/ServerOutputs.txt";
    static String ServerUptimePath = System.getProperty("user.dir").replace('\\', '/') + "/Server/Info/Uptime.txt";
    static String BlockedDevices = System.getProperty("user.dir").replace('\\', '/') + "/Server/Info/BlockedDevices.txt";
    static String ConnectedDevicesPath = System.getProperty("user.dir").replace('\\', '/') + "/Server/Info/ConnectedDevices.txt";
    static long serverUptime = 0;
    static int usedPortNumber = 0;
    static Boolean SingleMouseController = true;

    public static void main(String[] args) throws Exception{
        // Json data extracting

        String json = new String(Files.readAllBytes(Paths.get(ConfigurationFilePath)));

        json = json.replace("{", "").replace("}", "").replace("\"", "");

        String[] parts = json.split(",");

        for (String part : parts) {
            String[] keyValue = part.split(": ");

            String key = keyValue[0].trim();
            String value = keyValue[1].trim();

            if (key.equals("SSLCertificateKeyStorePath")){
                SSLCertificateKeyStorePath = value;
            } else if (key.equals("WebApplicationPath")){
                WebApplicationPath = value;
            } else if (key.equals("Key")){
                Key = value;
            } else if (key.equals("PORT")){
                usedPortNumber = Integer.parseInt(value);
            }else if (key.equals("SingleMouseController")){
                SingleMouseController = Boolean.parseBoolean(value);
            }
        }

        // SSL Configuration

        char[] keystorePassword = "12345678".toCharArray();
        KeyStore ks = KeyStore.getInstance("PKCS12");
        FileInputStream fis = new FileInputStream(SSLCertificateKeyStorePath);
        ks.load(fis, keystorePassword);

        KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
        kmf.init(ks, keystorePassword);

        SSLContext sslContext = SSLContext.getInstance("TLS");

        sslContext.init(kmf.getKeyManagers(), null, null);

        // Create HttpsServer server
        Integer portNumber = usedPortNumber;
        HttpsServer server = HttpsServer.create(new InetSocketAddress("0.0.0.0", portNumber), 0);
        server.setHttpsConfigurator(new HttpsConfigurator(sslContext) {
            @Override
            public void configure(HttpsParameters params) {

                try {
                    SSLContext c = getSSLContext();
                    /*SSLEngine engine = c.createSSLEngine();
                    params.setNeedClientAuth(false);
                    params.setCipherSuites(engine.getEnabledCipherSuites());
                    params.setProtocols(engine.getEnabledProtocols());*/
                    SSLParameters defaultSSLParameters = c.getDefaultSSLParameters();
                    params.setSSLParameters(defaultSSLParameters);

                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            }
        });

        // Create endpoint "/"
        server.createContext("/", new MyHandler());


        // Create endpoint "/data"
        server.createContext("/data", exchange ->{
            System.out.println("Incoming request -> [RequestURI: " + exchange.getRequestURI() + "]" + " " + "[RequestMethod: " + exchange.getRequestMethod() + "]" + " " + "[" + "Remote Address: " + exchange.getRemoteAddress().getAddress().getHostAddress() + "]");

            if ("POST".equals(exchange.getRequestMethod())){
                InputStream is = exchange.getRequestBody();
                String body = new String(is.readAllBytes());
                //System.out.println("Received: " + body);

                // Send data to MouseMover Class
                MouseMover ReceiverClass = new MouseMover();

                try {
                    MouseMover.ReceiveData(body);
                } catch (Exception e) {
                    e.printStackTrace();
                }


                String response = "Data received!";

                exchange.sendResponseHeaders(200, response.getBytes().length);
                OutputStream os = exchange.getResponseBody();
                os.write(response.getBytes());
                os.close();
            }else{
                exchange.sendResponseHeaders(405, -1); // Method Not Allowed
            }
        });

        // Create endpoint "/health-check"
        server.createContext("/health-check", exchange ->{
            System.out.println("Incoming request -> [RequestURI: " + exchange.getRequestURI() + "]" + " " + "[RequestMethod: " + exchange.getRequestMethod() + "]" + " " + "[" + "Remote Address: " + exchange.getRemoteAddress().getAddress().getHostAddress() + "]");

            if ("POST".equals(exchange.getRequestMethod())){
                String response = "Can't complain!";

                exchange.sendResponseHeaders(200, response.getBytes().length);
                OutputStream os = exchange.getResponseBody();
                os.write(response.getBytes());
                os.close();
            }else{
                exchange.sendResponseHeaders(405, -1); // Method Not Allowed
            }
        });

        // Create endpoint "/shutdownserver-passKey"
        server.createContext("/shutdownserver-" + Key, exchange ->{
            System.out.println("Incoming request -> [RequestURI: " + exchange.getRequestURI() + "]" + " " + "[RequestMethod: " + exchange.getRequestMethod() + "]" + " " + "[" + "Remote Address: " + exchange.getRemoteAddress().getAddress().getHostAddress() + "]");

            if ("POST".equals(exchange.getRequestMethod())){
                String response = "Okay, bye!";

                exchange.sendResponseHeaders(200, response.getBytes().length);
                OutputStream os = exchange.getResponseBody();
                os.write(response.getBytes());
                os.close();

                // Send signal to MouseMover Class
                MouseMover ReceiverClass = new MouseMover();

                try {
                    MouseMover.ReceiveData("CloseServer");
                } catch (Exception e) {
                    e.printStackTrace();
                }

                try {
                    FileWriter writer = new FileWriter(ConnectedDevicesPath);
                    writer.write("");
                    writer.close();
                } catch (Exception e) {
                    e.printStackTrace();
                }

                server.stop(0);
                Runtime.getRuntime().halt(0);
            }else{
                exchange.sendResponseHeaders(405, -1); // Method Not Allowed
            }
        });

        // Create endpoint "/login-passKey"
        server.createContext("/login-" + Key, exchange ->{
            System.out.println("Incoming request -> [RequestURI: " + exchange.getRequestURI() + "]" + " " + "[RequestMethod: " + exchange.getRequestMethod() + "]" + " " + "[" + "Remote Address: " + exchange.getRemoteAddress().getAddress().getHostAddress() + "]");

            if ("POST".equals(exchange.getRequestMethod())){
                String response = "Access permitted!";

                InputStream is = exchange.getRequestBody();
                String data = new String(is.readAllBytes());
                String deviceIp = exchange.getRemoteAddress().getAddress().getHostAddress();

                System.out.println("A user got access to the full web application | " + deviceIp + " | " + data);

                exchange.sendResponseHeaders(200, response.getBytes().length);
                OutputStream os = exchange.getResponseBody();
                os.write(response.getBytes());
                os.close();

                FileWriter writer = new FileWriter(LastVisitsLogPath, true);
                String time = "[" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + "]";

                writer.write(time + " A user got access to the full web application | " + deviceIp + " | " + data + "\n");
                writer.close();
            }else{
                exchange.sendResponseHeaders(405, -1); // Method Not Allowed
            }
        });

        // Create endpoint "/checkconnected"
        server.createContext("/checkconnected", exchange ->{
            System.out.println("Incoming request -> [RequestURI: " + exchange.getRequestURI() + "]" + " " + "[RequestMethod: " + exchange.getRequestMethod() + "]" + " " + "[" + "Remote Address: " + exchange.getRemoteAddress().getAddress().getHostAddress() + "]");

            if ("POST".equals(exchange.getRequestMethod())){
                String response = "Ok";

                InputStream is = exchange.getRequestBody();

                String data = new String(is.readAllBytes());
                String deviceIp = exchange.getRemoteAddress().getAddress().getHostAddress();

                String targetLine = "[" + deviceIp + " | " + data + "]";

                BufferedReader reader = new BufferedReader(new FileReader(BlockedDevices));
                String line;
                Boolean isUserBlocked = false;
                Boolean isUserKicked = false;

                while ((line = reader.readLine()) != null) {
                    if (line.endsWith(targetLine)){
                        isUserBlocked = true;
                    }else if (line.endsWith(targetLine + "+")){
                        isUserKicked = true;
                    }
                }

                reader.close();

                if (isUserBlocked){
                    response = "You're blocked!";
                }else if(isUserKicked){
                    response = "You're kicked!";
                }

                if (!isUserBlocked){
                reader = new BufferedReader(new FileReader(ConnectedDevicesPath));
                line = "";
                String editedLines = "";

                Boolean addOrNot = true;
                Boolean controllerOrNot = false;

                while ((line = reader.readLine()) != null) {
                    try {
                        if (line.equals("")){
                            continue;
                        }
                    int index = line.replace("]*", "]").indexOf(" -- ");
                    String unixTimeStamp = line.replace("]*", "]").substring(index + 4).trim();
                    String deviceData = line.replace("]*", "]").substring(0, index).trim();


                    if (deviceData.endsWith(targetLine) || deviceData.endsWith(targetLine + "*")){
                        addOrNot = false;

                        String currentUnixTimeStamp = String.valueOf(System.currentTimeMillis());
                        editedLines += deviceData + " -- " + currentUnixTimeStamp + "\n";
                    }else{
                        editedLines += line.replace("\n", "") + "\n";
                    }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }

                }

                reader.close();

                for (String eLine : editedLines.split("\n")){
                    if (eLine.contains(targetLine + "*")){
                        controllerOrNot = true;
                    }
                }

                String fullEditedLines = "";
                if (!editedLines.contains("]*")){
                    for (String eLine : editedLines.split("\n")){
                        if (eLine.contains(targetLine)){
                            controllerOrNot = true;
                            int index = eLine.replace("]*", "]").indexOf(" -- ");
                            String deviceData = eLine.replace("]*", "]").substring(0, index).trim();
                            String currentUnixTimeStamp = String.valueOf(System.currentTimeMillis());
                            fullEditedLines += deviceData + "*" + " -- " + currentUnixTimeStamp + "\n";
                        }else{
                            fullEditedLines += eLine.replace("\n", "") + "\n";
                        }
                    }
                }

                if (fullEditedLines.replace("\n", "").equals("")){
                    fullEditedLines = editedLines;
                }

                if (SingleMouseController) {
                    if (controllerOrNot){
                        if (!isUserBlocked && !isUserKicked){
                            response = "Controller";
                        }
                    }else{
                        if (!isUserBlocked && !isUserKicked){
                            response = "NotController";
                        }
                    }
                }

                if (!fullEditedLines.replace("\n", "").equals("")){
                    FileWriter writerDel = new FileWriter(ConnectedDevicesPath);
                    writerDel.write(fullEditedLines);
                    writerDel.close();
                }

                if (addOrNot) {
                    String time = "[" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + "]";

                    FileWriter writer = new FileWriter(ConnectedDevicesPath, true);
                    String unixTimeStamp = String.valueOf(System.currentTimeMillis());
                    writer.write(time + " " + targetLine + " -- " + unixTimeStamp + "\n");
                    writer.close();
                }
                }

                exchange.sendResponseHeaders(200, response.getBytes().length);
                OutputStream os = exchange.getResponseBody();
                os.write(response.getBytes());
                os.close();
            }else{
                exchange.sendResponseHeaders(405, -1); // Method Not Allowed
            }
        });

        // Start server
        server.setExecutor(null);
        server.start();

        System.out.println("Server started at https://" + InetAddress.getLocalHost().getHostAddress() + ":" + String.valueOf(portNumber) + "/ or https://localhost:" + String.valueOf(portNumber) + "/");
        try {
            FileWriter writer = new FileWriter(ServerUptimePath);
            writer.write("00:00:00");
            writer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        Thread thread = new Thread(() -> {
        while (true) {
            try {
                BufferedReader reader = new BufferedReader(new FileReader(ConnectedDevicesPath));
                String line;
                String linesToStay = "";

                while ((line = reader.readLine()) != null) {
                    try {
                        if (line.equals("")){
                            continue;
                        }

                        int index = line.indexOf(" -- ");

                        String unixTimeStamp = line.substring(index + 4).trim();
                        String deviceData = line.substring(0, index).trim().replace("*", "");

                        long currentUnixTimeStamp = System.currentTimeMillis();
                        long changeRate = currentUnixTimeStamp - (Long.parseLong(unixTimeStamp));

                        if (changeRate <= 3000){
                            linesToStay += line.replace("\n", "") + "\n";
                        }else{
                            System.out.println("A user has just left | " + deviceData.split("] ")[1]);

                            String time = "[" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + "]";

                            FileWriter writer = new FileWriter(LastVisitsLogPath, true);
                            writer.write(time + " " + "A user has just left | " + deviceData.split("] ")[1] + "\n");
                            writer.close();
                        }

                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
                reader.close();

                FileWriter writer = new FileWriter(ConnectedDevicesPath);

                writer.write(linesToStay);
                writer.close();

                Thread.sleep(3000);
            } catch (Exception e) {
                e.printStackTrace();
            }


        }
    });

    Thread upTimeThread = new Thread(() -> {
        while (true) {
            try {
                long hours = serverUptime / 3600;
                long minutes = (serverUptime % 3600) / 60;
                long seconds = serverUptime % 60;

                String fullUptime = String.format("%02d:%02d:%02d", hours, minutes, seconds);

                FileWriter writer = new FileWriter(ServerUptimePath);
                writer.write(fullUptime);
                writer.close();

                serverUptime += 1;

                Thread.sleep(1000);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    });

    thread.start();
    upTimeThread.start();
    }

    static class MyHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            System.out.println("Incoming request -> [RequestURI: " + exchange.getRequestURI() + "]" + " " + "[RequestMethod: " + exchange.getRequestMethod() + "]" + " " + "[" + "Remote Address: " + exchange.getRemoteAddress().getAddress().getHostAddress() + "]");
            String path = exchange.getRequestURI().getPath();
            String deviceIp = exchange.getRemoteAddress().getAddress().getHostAddress();

            if(path.equals("/")){
                path = "index.html";

                System.out.println("A new visit +1" + " | " + deviceIp);

                FileWriter writer = new FileWriter(LastVisitsLogPath, true);
                String time = "[" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + "]";

                writer.write(time + " A new visit +1" + " | " + deviceIp + "\n");
                writer.close();
            }

            File file = new File(WebApplicationPath + path);

            if (!file.exists()){
                if (path.startsWith("/wrongKey-")){
                    String wrongPassKey = path.replace("/wrongKey-", "");

                    InputStream is = exchange.getRequestBody();
                    String data = new String(is.readAllBytes());

                    System.out.println("A user entered a wrong access key! '" + wrongPassKey + "' | " + deviceIp + " | " + data);

                    String response = "Access denied, wrong access key!";
                    exchange.sendResponseHeaders(401, response.length());
                    exchange.getResponseBody().write(response.getBytes());

                    FileWriter writer = new FileWriter(LastVisitsLogPath, true);
                    String time = "[" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + "]";

                    writer.write(time + " A user entered a wrong access key! '" + wrongPassKey + "' | " + deviceIp + " | " + data + "\n");
                    writer.close();
                }else{
                    if (!path.startsWith("/login-")){
                        System.out.println("A user tried to go to an unknown page '" + path + "' | " + deviceIp);
                        String response = "404 Not Found";
                        exchange.sendResponseHeaders(404, response.length());
                        exchange.getResponseBody().write(response.getBytes());

                        FileWriter writer = new FileWriter(LastVisitsLogPath, true);
                        String time = "[" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + "]";

                        writer.write(time + " A user tried to go to an unknown page '" + path + "' | " + deviceIp + "\n");
                        writer.close();
                    }

                    if (path.startsWith("/login-")){
                        String passKey = path.replace("/login-", "");

                        if (!passKey.equals(Key)){
                        String response = "Access denied, wrong access key!";
                        exchange.sendResponseHeaders(401, response.length());
                        exchange.getResponseBody().write(response.getBytes());
                        }
                    }
                }
            }else{
                byte[] response = java.nio.file.Files.readAllBytes(file.toPath());

                String contentType = getContentType(file.getName());
                exchange.getResponseHeaders().add("Content-Type", contentType);
                exchange.sendResponseHeaders(200, response.length);
                exchange.getResponseBody().write(response);
            }
            exchange.close();

        }
    }

    public static String getContentType(String fileName){
        if (fileName.endsWith(".html")) return "text/html";
        if (fileName.endsWith(".js")) return "application/javascript";
        if (fileName.endsWith(".css")) return "text/css";
       return "text/plain";
    }

}