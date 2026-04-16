export default {
    // Global
    appName: 'Arloupe Enterprise',
    appSubtitle: '牙科影像管理平台',
    logout: '登出',
    darkMode: '深色模式',
    lightMode: '淺色模式',
    language: '語言',

    // Login
    login: {
        selectPortal: '選擇存取入口',
        adminAccess: '管理員入口',
        adminDesc: '系統設定、使用者帳號、安全策略',
        clinicalStaff: '臨床人員',
        staffDesc: '牙醫師與洗牙師 — 瀏覽、搜尋、剪輯影片',
        patientPortal: '病患入口',
        patientDesc: '查看經核准的牙科治療影片',
        footer: '僅限授權臨床人員與病患使用。',
        footerHipaa: '此連線受 HIPAA 合規性監控。'
    },

    // Sidebar
    sidebar: {
        medicalViewer: '臨床檢視器',
        managementConsole: '管理後台'
    },

    // Clinical Viewer
    viewer: {
        title: '臨床檢視器',
        subtitle: '歷史影片紀錄',
        searchPlaceholder: '搜尋病患姓名或 ID...',
        searchFilters: '搜尋篩選條件',
        clear: '清除',
        treatmentType: '治療類型',
        allTreatments: '所有治療',
        cleaning: '洗牙 / 刮治',
        extraction: '拔牙',
        implant: '植牙手術',
        dateRange: '日期範圍',
        patientRecordings: '病患治療錄影',
        noRecords: '找不到符合篩選條件的紀錄。',
        hipaaTitle: 'HIPAA 驗證 (Gemini AI)',
        runScan: '執行 AI 安全掃描'
    },

    // Video Player
    player: {
        noVideoSelected: '未選擇影片',
        selectRecording: '請選擇一段錄影紀錄',
        share: '分享',
        shareTitle: '分享錄影',
        copyLink: '複製內部連結',
        copyLinkDesc: '透過連結分享給臨床人員',
        linkCopied: '✓ 已複製連結！',
        sendToStaff: '傳送給同事',
        sendToStaffDesc: '直接通知同事',
        generatePatientLink: '產生病患連結',
        generatePatientLinkDesc: '限時安全連結，用於病患入口',
        clipEditor: '影片剪輯器',
        clipEditorDesc: '建立影片片段以供分享或匯出',
        collapse: '收合',
        expand: '展開',
        startTime: '開始時間',
        endTime: '結束時間',
        createClip: '建立片段',
        preview: '預覽',
        savedClips: '已儲存片段',
        deleteClip: '刪除',
        recorded: '錄製日期',
        duration: '長度'
    },

    // Management
    management: {
        title: '管理儀表板',
        subtitle: '系統管理 & 安全總覽',
        createPolicy: '建立新策略',
        totalPatients: '病患總數',
        cloudStorage: '雲端儲存',
        dailyScans: '每日掃描',
        securityThreats: '安全威脅',
        activeUsers: '系統使用者',
        activeUsersDesc: '診所人員 & 員工帳號',
        viewAll: '檢視全部',
        securityHealth: '安全健康度',
        hipaaCompliance: 'HIPAA 合規性',
        strongProtection: '防護啟用中',
        securityPolicies: '安全策略',
        twoFA: '雙因素驗證',
        twoFADesc: '所有人員必須啟用',
        encryption: '資料加密',
        encryptionDesc: 'AES-256 影片雲端加密',
        timeout: '自動逾時登出',
        timeoutDesc: '閒置 10 分鐘後登出',
        ipWhitelist: 'IP 白名單',
        ipWhitelistDesc: '限制診所內部網路',
        inspectLog: '檢視日誌'
    },

    // Audit Table
    audit: {
        timestamp: '時間戳記',
        user: '使用者',
        action: '操作',
        status: '狀態',
        details: '詳情'
    },

    // Patient Portal
    patient: {
        welcomeBack: '歡迎回來，',
        approvedContent: '您的核准內容',
        readyToPlay: '準備播放',
        saveFile: '儲存檔案',
        healthStatus: '健康狀態',
        treatmentPlan: '治療計畫',
        onTrack: '進度正常 • 下次回診：4月25日',
        requestAppointment: '預約掛號',
        support: '支援與幫助',
        chatWithStaff: '與診所人員對話',
        chatResponse: '平均回覆時間：5 分鐘'
    }
};
