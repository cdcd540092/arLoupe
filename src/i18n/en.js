export default {
    // Global
    appName: 'Arloupe Enterprise',
    appSubtitle: 'Dental Imaging Platform',
    logout: 'Sign Out',
    darkMode: 'Dark Mode',
    lightMode: 'Light Mode',
    language: 'Language',

    // Login
    login: {
        selectPortal: 'Select Access Portal',
        adminAccess: 'Admin Access',
        adminDesc: 'System settings, user accounts, security',
        clinicalStaff: 'Clinical Staff',
        staffDesc: 'Dentist & hygienist — view, search, clip videos',
        patientPortal: 'Patient Portal',
        patientDesc: 'View approved dental procedure recordings',
        footer: 'Authorized clinical staff and patients only.',
        footerHipaa: 'This session is monitored for HIPAA compliance.'
    },

    // Sidebar
    sidebar: {
        liveStream: 'Live Stream',
        medicalViewer: 'Medical Viewer',
        managementConsole: 'Management Console'
    },

    // Live Stream
    live: {
        title: 'Real-time Video Feed',
        subtitle: 'arLoupe Camera Live Stream',
        startRecording: 'START RECORDING',
        stopRecording: 'STOP RECORDING',
        captureFrame: 'CAPTURE FRAME',
        offline: 'Camera Offline',
        offlineDesc: 'Please check arLoupe connection or network settings.'
    },

    // Clinical Viewer
    viewer: {
        title: 'Clinical Viewer',
        subtitle: 'Historical Video Records',
        searchPlaceholder: 'Search by Patient Name or ID...',
        searchFilters: 'Search Filters',
        clear: 'Clear',
        treatmentType: 'Treatment Type',
        allTreatments: 'All Treatments',
        cleaning: 'Cleaning / Scaler',
        extraction: 'Extraction',
        implant: 'Implant Surgery',
        dateRange: 'Date Range',
        patientRecordings: 'Patient Recordings',
        noRecords: 'No records found matching filters.',
        hipaaTitle: 'HIPAA Verification (Gemini AI)',
        runScan: 'RUN AI SECURITY SCAN'
    },

    // Video Player
    player: {
        noVideoSelected: 'No Video Selected',
        selectRecording: 'Select a recording to begin',
        share: 'SHARE',
        shareTitle: 'Share Recording',
        copyLink: 'Copy Internal Link',
        copyLinkDesc: 'Share with clinical staff via link',
        linkCopied: '✓ Link Copied!',
        sendToStaff: 'Send to Staff Member',
        sendToStaffDesc: 'Notify a colleague directly',
        generatePatientLink: 'Generate Patient Link',
        generatePatientLinkDesc: 'Time-limited secure link for patient portal',
        clipEditor: 'Clip Editor',
        clipEditorDesc: 'Create video segments for sharing or export',
        collapse: 'COLLAPSE',
        expand: 'EXPAND',
        startTime: 'Start Time',
        endTime: 'End Time',
        createClip: 'CREATE CLIP',
        preview: 'Preview',
        savedClips: 'Saved Clips',
        deleteClip: 'DELETE',
        recorded: 'Recorded',
        duration: 'Duration',
        downloadVideo: 'DOWNLOAD VIDEO',
        exportMp4: 'EXPORT MP4',
        saveToCloud: 'SAVE TO CLOUD',
        processing: 'PROCESSING...',
        saved: 'SAVED',
        renameClip: 'Rename Clip',
        renameDesc: 'Set an easily identifiable name for the clip to display in the patient record list.',
        enterClipName: 'Enter clip name...',
        cancel: 'Cancel',
        confirmSave: 'Confirm Save'
    },

    // Management
    management: {
        title: 'Management Dashboard',
        subtitle: 'System Admin & Security Overview',
        createPolicy: 'CREATE NEW POLICY',
        totalPatients: 'Total Patients',
        cloudStorage: 'Cloud Storage',
        dailyScans: 'Daily Scans',
        securityThreats: 'Security Threats',
        activeUsers: 'Active System Users',
        activeUsersDesc: 'Clinic Personnel & Staff Accounts',
        viewAll: 'View All',
        securityHealth: 'Security Health',
        hipaaCompliance: 'HIPAA Compliance',
        strongProtection: 'Protection Active',
        securityPolicies: 'Security Policies',
        twoFA: '2FA Enforcement',
        twoFADesc: 'Required for all staff',
        encryption: 'Data Encryption',
        encryptionDesc: 'AES-256 for video cloud',
        timeout: 'Automatic Timeout',
        timeoutDesc: 'Exit after 10m inactivity',
        ipWhitelist: 'IP Whitelisting',
        ipWhitelistDesc: 'Restrict to local clinic network',
        inspectLog: 'Inspect Log'
    },

    // Audit Table
    audit: {
        timestamp: 'Timestamp',
        user: 'User',
        action: 'Action',
        status: 'Status',
        details: 'Details'
    },

    // Patient Portal
    patient: {
        welcomeBack: 'Welcome back,',
        approvedContent: 'YOUR APPROVED CONTENT',
        readyToPlay: 'Ready to Play',
        saveFile: 'Save File',
        healthStatus: 'Health Status',
        treatmentPlan: 'Treatment Plan',
        onTrack: 'On Track • Next Visit: April 25',
        requestAppointment: 'REQUEST APPOINTMENT',
        support: 'Support & Help',
        chatWithStaff: 'Chat with Staff',
        chatResponse: 'Average response: 5m'
    }
};
