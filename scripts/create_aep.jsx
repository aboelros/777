var log = new File("C:/Users/ARKAN STOER/Desktop/777/ae_debug.log");
log.open("w");
log.writeln("ExtendScript execution started at " + new Date().toString());
try {
    app.newProject();
    var comp = app.project.items.addComp("TestComp", 1920, 1080, 1.0, 5.0, 30.0);
    var txt = comp.layers.addText("AI Sales Commander - Meta Review");
    var saveTarget = new File("C:/Users/ARKAN STOER/Desktop/777/test_ae_proj.aep");
    app.project.save(saveTarget);
    log.writeln("Successfully saved AEP project to: " + saveTarget.fsName);
} catch (e) {
    log.writeln("ExtendScript Error: " + e.toString());
}
log.close();
app.quit();
