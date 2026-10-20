// After Effects ExtendScript Builder for Meta App Review Videos
// Generates compositions, imports clips, applies animated title cards and permission overlays

(function() {
    var logFile = new File("C:/Users/ARKAN STOER/Desktop/777/ae_builder.log");
    logFile.open("w");
    logFile.writeln("=== After Effects Meta Screencast Generator Started ===");
    logFile.writeln("Timestamp: " + new Date().toString());

    try {
        app.newProject();
        logFile.writeln("New AE Project created.");

        var video1File = new File("C:/Users/ARKAN STOER/Desktop/777/meta_review_videos/video1_messaging_clip.mp4");
        var video2File = new File("C:/Users/ARKAN STOER/Desktop/777/meta_review_videos/video2_ads_leads_clip.mp4");
        var video3File = new File("C:/Users/ARKAN STOER/Desktop/777/meta_review_videos/video3_catalog_media_clip.mp4");

        if (!video1File.exists || !video2File.exists || !video3File.exists) {
            logFile.writeln("Error: Missing footage files.");
            logFile.close();
            app.quit();
            return;
        }

        var footage1 = app.project.importFile(new ImportOptions(video1File));
        var footage2 = app.project.importFile(new ImportOptions(video2File));
        var footage3 = app.project.importFile(new ImportOptions(video3File));
        logFile.writeln("Imported footage files successfully.");

        // COMPOSITION 1: Omnichannel Messaging & Customer Care
        var dur1 = (footage1.duration > 0 ? footage1.duration : 18.0) + 4.0;
        var comp1 = app.project.items.addComp("1_Messaging_and_Customer_Care", 1920, 1080, 1.0, dur1, 25.0);
        var fLayer1 = comp1.layers.add(footage1);
        fLayer1.startTime = 2.0;

        // Banner / Lower Third
        var textLayer1 = comp1.layers.addText("AI Sales Commander | Omnichannel Customer Care");
        var badgeLayer1 = comp1.layers.addText("PERMISSIONS: pages_messaging | instagram_manage_messages | whatsapp_business_messaging");
        logFile.writeln("Comp 1 built successfully.");

        // COMPOSITION 2: Meta Ads & Leads Retrieval
        var dur2 = (footage2.duration > 0 ? footage2.duration : 15.0) + 4.0;
        var comp2 = app.project.items.addComp("2_Ads_Analytics_and_Leads", 1920, 1080, 1.0, dur2, 25.0);
        var fLayer2 = comp2.layers.add(footage2);
        fLayer2.startTime = 2.0;

        var textLayer2 = comp2.layers.addText("AI Sales Commander | Ads Performance & CRM Leads");
        var badgeLayer2 = comp2.layers.addText("PERMISSIONS: leads_retrieval | ads_read | ads_management | Marketing API");
        logFile.writeln("Comp 2 built successfully.");

        // COMPOSITION 3: Commerce Catalog, WABA & Media
        var dur3 = (footage3.duration > 0 ? footage3.duration : 14.0) + 4.0;
        var comp3 = app.project.items.addComp("3_Catalog_WABA_and_Media", 1920, 1080, 1.0, dur3, 25.0);
        var fLayer3 = comp3.layers.add(footage3);
        fLayer3.startTime = 2.0;

        var textLayer3 = comp3.layers.addText("AI Sales Commander | Meta Catalog & Media Publishing");
        var badgeLayer3 = comp3.layers.addText("PERMISSIONS: catalog_management | business_management | whatsapp_business_management | publish_video");
        logFile.writeln("Comp 3 built successfully.");

        // Save project
        var aepFile = new File("C:/Users/ARKAN STOER/Desktop/777/meta_app_review_showcase.aep");
        app.project.save(aepFile);
        logFile.writeln("Saved AEP project to: " + aepFile.fsName);

    } catch (e) {
        logFile.writeln("Exception in AE Script: " + e.toString());
    }

    logFile.writeln("=== AE Build Completed ===");
    logFile.close();
    app.quit();
})();
