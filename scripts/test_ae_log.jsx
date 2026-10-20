try {
    var logFile = new File("C:/Users/ARKAN STOER/Desktop/777/ae_log.txt");
    logFile.open("w");
    logFile.writeln("Script started: " + new Date().toString());
    app.newProject();
    var comp = app.project.items.addComp("TestComp", 1920, 1080, 1, 3, 30);
    var saveFile = new File("C:/Users/ARKAN STOER/Desktop/777/test_ae.aep");
    app.project.save(saveFile);
    logFile.writeln("Saved project successfully to " + saveFile.fsName);
    logFile.close();
    app.quit();
} catch (e) {
    var errFile = new File("C:/Users/ARKAN STOER/Desktop/777/ae_error.txt");
    errFile.open("w");
    errFile.writeln("Error: " + e.toString());
    errFile.close();
    app.quit();
}
