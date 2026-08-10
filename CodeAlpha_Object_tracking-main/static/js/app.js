document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const views = {
        dashboard: document.getElementById('view-dashboard'),
        sessions: document.getElementById('view-sessions'),
        settings: document.getElementById('view-settings')
    };
    const navItems = document.querySelectorAll('.nav-item');

    // Controls
    const btnStartCam = document.getElementById('btn-start-cam');
    const btnStopCam = document.getElementById('btn-stop-cam');
    const uploadInput = document.getElementById('video-upload');
    const uploadText = document.getElementById('upload-text');
    const btnStartVid = document.getElementById('btn-start-vid');
    const btnStopVid = document.getElementById('btn-stop-vid');
    
    // Actions
    const btnScreenshot = document.getElementById('btn-screenshot');
    const btnStartRec = document.getElementById('btn-start-rec');
    const btnStopRec = document.getElementById('btn-stop-rec');

    // Video Feed
    const videoFeed = document.getElementById('video-feed');
    const videoOverlay = document.getElementById('video-overlay');

    // Status Badges
    const badgeCam = document.getElementById('badge-camera');
    const badgeYolo = document.getElementById('badge-yolo');
    const badgeRec = document.getElementById('badge-record');
    
    // Stats
    const statFps = document.getElementById('stat-fps');
    const statTracked = document.getElementById('stat-tracked');
    const statInf = document.getElementById('stat-inference');
    const statDet = document.getElementById('stat-detections');

    // Detailed Stats
    const detAvgConf = document.getElementById('det-avg-conf');
    const detFps = document.getElementById('det-fps');
    const detInfTime = document.getElementById('det-inf-time');
    const detTotalDet = document.getElementById('det-total-det');
    const detTracked = document.getElementById('det-tracked');
    const detProcTime = document.getElementById('det-proc-time');
    const detInput = document.getElementById('det-input');
    const detSession = document.getElementById('det-session');

    // Objects List
    const objectsTbody = document.getElementById('objects-tbody');

    // System Status
    const sysCam = document.getElementById('sys-cam');
    const sysYolo = document.getElementById('sys-yolo');
    const sysTracker = document.getElementById('sys-tracker');
    const sysRec = document.getElementById('sys-rec');
    const sysBack = document.getElementById('sys-back');

    // Polling Interval
    let statusInterval = null;
    let selectedVideoPath = null;

    // ----- NAVIGATION -----
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            
            const target = item.dataset.target;
            Object.values(views).forEach(v => v.style.display = 'none');
            views[target].style.display = 'block';

            if(target === 'sessions') {
                loadSessions();
            }
        });
    });

    // ----- STATUS POLLING -----
    function startPolling() {
        if(statusInterval) clearInterval(statusInterval);
        statusInterval = setInterval(fetchStatus, 1000);
    }

    async function fetchStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            updateDashboard(data);
        } catch (err) {
            console.error("Status fetch failed", err);
            document.getElementById('sys-pulse').className = 'pulse-dot red';
            document.getElementById('sys-status-text').innerText = 'Backend Offline';
        }
    }

    async function updateDashboard(data) {
        // System Status
        document.getElementById('sys-pulse').className = 'pulse-dot green';
        document.getElementById('sys-status-text').innerText = 'System Online';

        // Badges
        if (data.camera_status) {
            badgeCam.classList.add('active');
            badgeCam.querySelector('span').innerText = 'Connected';
        } else {
            badgeCam.classList.remove('active');
            badgeCam.querySelector('span').innerText = 'Disconnected';
        }

        if (data.yolo_status) {
            badgeYolo.classList.add('active');
            badgeYolo.querySelector('span').innerText = 'Model Ready';
        } else {
            badgeYolo.classList.remove('active');
            badgeYolo.querySelector('span').innerText = 'Model Idle';
        }

        if (data.recording_status) {
            badgeRec.classList.add('active', 'recording');
            badgeRec.querySelector('span').innerText = 'Recording';
            btnStartRec.disabled = true;
            btnStopRec.disabled = false;
        } else {
            badgeRec.classList.remove('active', 'recording');
            badgeRec.querySelector('span').innerText = 'Rec Off';
            btnStartRec.disabled = false;
            btnStopRec.disabled = true;
        }

        // Stream Visibility
        if (data.camera_status || data.processing_status) {
            // Processing is likely running
            if(videoFeed.src.indexOf('/video-feed') === -1) {
                videoFeed.src = '/video-feed?' + new Date().getTime();
                videoFeed.style.display = 'block';
                videoOverlay.style.display = 'none';
            }
            // Enable stop buttons, disable starts
            btnStartCam.disabled = true;
            btnStopCam.disabled = false;
            btnStartVid.disabled = true;
            btnStopVid.disabled = false;
        } else {
            videoFeed.src = '';
            videoFeed.style.display = 'none';
            videoOverlay.querySelector('p').innerText = 'No active video stream.';
            videoOverlay.style.display = 'flex';
            
            btnStartCam.disabled = false;
            btnStopCam.disabled = true;
            btnStartVid.disabled = !selectedVideoPath;
            btnStopVid.disabled = true;
        }

        // Stats
        statFps.innerText = data.fps !== null ? data.fps : '0.0';
        statTracked.innerText = data.tracked_objects !== null ? data.tracked_objects : '0';
        statInf.innerText = data.inference_time !== null ? data.inference_time + 'ms' : '0ms';
        statDet.innerText = data.total_detections !== null ? data.total_detections : '0';

        // Detailed Stats
        detAvgConf.innerText = data.avg_confidence !== null ? data.avg_confidence + '%' : 'N/A';
        detFps.innerText = data.fps !== null ? data.fps : 'N/A';
        detInfTime.innerText = data.inference_time !== null ? data.inference_time + ' ms' : 'N/A';
        detTotalDet.innerText = data.total_detections !== null ? data.total_detections : 'N/A';
        detTracked.innerText = data.tracked_objects !== null ? data.tracked_objects : 'N/A';
        detProcTime.innerText = data.processing_time !== null ? data.processing_time + ' s' : 'N/A';
        detInput.innerText = data.current_input !== null ? data.current_input : 'N/A';
        detSession.innerText = data.current_session_id !== null ? '#' + data.current_session_id : 'N/A';
        // System Status Panel
        sysBack.innerText = 'Connected';
        sysBack.className = 'status-badge completed';
        
        sysCam.innerText = data.camera_status ? 'Connected' : 'Disconnected';
        sysCam.className = data.camera_status ? 'status-badge completed' : 'status-badge stopped';
        
        sysYolo.innerText = data.yolo_status ? 'Loaded' : 'Not Loaded';
        sysYolo.className = data.yolo_status ? 'status-badge completed' : 'status-badge stopped';
        
        sysTracker.innerText = data.tracker_status ? 'Active' : 'Inactive';
        sysTracker.className = data.tracker_status ? 'status-badge completed' : 'status-badge stopped';
        
        sysRec.innerText = data.recording_status ? 'Recording' : 'Not Recording';
        sysRec.className = data.recording_status ? 'status-badge recording' : 'status-badge stopped';

        // Fetch Detections separately
        try {
            const detRes = await fetch('/api/detections');
            const detData = await detRes.json();
            if (detData && detData.length > 0) {
                objectsTbody.innerHTML = detData.map(obj => `
                    <tr>
                        <td>${obj.tracking_id}</td>
                        <td>${obj.class_name}</td>
                        <td class="text-success">${(obj.confidence * 100).toFixed(1)}%</td>
                        <td>${obj.status || 'Tracking'}</td>
                        <td>N/A</td>
                    </tr>
                `).join('');
            } else {
                objectsTbody.innerHTML = '<tr><td colspan="5" class="empty-list">No objects currently tracked.</td></tr>';
            }
        } catch(e) {
            console.error("Error fetching detections");
        }
    }

    // ----- CONTROLS -----
    
    // Notifications helper
    const toast = Swal.mixin({
        toast: true, position: 'top-end', showConfirmButton: false, timer: 3000,
        background: 'rgba(24, 24, 27, 0.9)', color: '#fff',
        customClass: { popup: 'glass-card' }
    });

    btnStartCam.addEventListener('click', async () => {
        const originalText = btnStartCam.innerHTML;
        btnStartCam.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Starting Camera...';
        btnStartCam.disabled = true;
        try {
            const res = await fetch('/api/start-camera', { method: 'POST' });
            const data = await res.json();
            if(data.success) toast.fire({ icon: 'success', title: 'Camera started successfully.' });
            else toast.fire({ icon: 'error', title: data.message });
        } catch(e) { toast.fire({ icon: 'error', title: 'Unable to connect to backend.' }); }
        finally { btnStartCam.innerHTML = originalText; }
    });

    btnStopCam.addEventListener('click', async () => {
        const originalText = btnStopCam.innerHTML;
        btnStopCam.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Stopping Camera...';
        btnStopCam.disabled = true;
        try {
            const res = await fetch('/api/stop-camera', { method: 'POST' });
            const data = await res.json();
            if(data.success) toast.fire({ icon: 'info', title: 'Processing stopped.' });
        } catch(e) { toast.fire({ icon: 'error', title: 'Unable to connect to backend.' }); }
        finally { btnStopCam.innerHTML = originalText; }
    });

    // Upload
    const uploadBox = document.querySelector('.upload-box');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadBox.addEventListener(eventName, preventDefaults, false);
    });
    function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadBox.addEventListener(eventName, () => uploadBox.classList.add('highlight'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        uploadBox.addEventListener(eventName, () => uploadBox.classList.remove('highlight'), false);
    });
    
    uploadBox.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if(files.length > 0) handleFile(files[0]);
    });
    
    document.getElementById('video-upload').addEventListener('change', (e) => {
        if(e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if(!['mp4', 'avi', 'mov', 'mkv'].includes(ext)) {
            toast.fire({ icon: 'error', title: 'Invalid video format. (mp4, avi, mov, mkv allowed)' });
            return;
        }
        if(file.size > 100 * 1024 * 1024) { // 100 MB max client check
            toast.fire({ icon: 'error', title: 'File too large. Max 100MB allowed.' });
            return;
        }
        document.getElementById('upload-text').innerText = file.name;
        selectedVideoFile = file;
        
        // Actually trigger the upload
        handleFileUpload(file);
    }

    async function handleFileUpload(file) {
        if(!file) return;
        uploadText.innerText = 'Uploading...';
        
        const formData = new FormData();
        formData.append('video', file);

        try {
            const res = await fetch('/api/upload-video', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if(data.success) {
                selectedVideoPath = data.filepath;
                uploadText.innerText = file.name;
                toast.fire({ icon: 'success', title: 'Video uploaded successfully.' });
                btnStartVid.disabled = false;
            } else {
                uploadText.innerText = 'Upload Failed';
                toast.fire({ icon: 'error', title: data.message });
            }
        } catch(e) {
            uploadText.innerText = 'Unable to connect to backend.';
        }
    }

    btnStartVid.addEventListener('click', async () => {
        if(!selectedVideoPath) return;
        
        const originalText = btnStartVid.innerHTML;
        btnStartVid.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Video...';
        btnStartVid.disabled = true;
        
        try {
            const res = await fetch('/api/start-processing', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filepath: selectedVideoPath })
            });
            const data = await res.json();
            if(data.success) toast.fire({ icon: 'success', title: 'Processing started.' });
            else toast.fire({ icon: 'error', title: data.message });
        } catch(e) {
            toast.fire({ icon: 'error', title: 'Unable to connect to backend.' });
        } finally {
            btnStartVid.innerHTML = originalText;
        }
    });

    btnStopVid.addEventListener('click', async () => {
        const originalText = btnStopVid.innerHTML;
        btnStopVid.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Stopping...';
        btnStopVid.disabled = true;
        try {
            const res = await fetch('/api/stop-processing', { method: 'POST' });
            const data = await res.json();
            if(data.success) toast.fire({ icon: 'info', title: 'Processing stopped.' });
        } catch(e) { toast.fire({ icon: 'error', title: 'Unable to connect to backend.' }); }
        finally { btnStopVid.innerHTML = originalText; }
    });

    // Actions
    btnScreenshot.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/screenshot', { method: 'POST' });
            const data = await res.json();
            if(data.success) toast.fire({ icon: 'success', title: 'Screenshot saved successfully.' });
            else toast.fire({ icon: 'error', title: data.message });
        } catch(e) { toast.fire({ icon: 'error', title: 'Unable to connect to backend.' }); }
    });

    btnStartRec.addEventListener('click', async () => {
        btnStartRec.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Starting Recording...';
        try {
            const res = await fetch('/api/start-recording', { method: 'POST' });
            const data = await res.json();
            if(data.success) toast.fire({ icon: 'success', title: 'Recording started.' });
            else toast.fire({ icon: 'error', title: data.message });
        } catch(e) { toast.fire({ icon: 'error', title: 'Unable to connect to backend.' }); }
        finally { btnStartRec.innerHTML = '<i class="fa-solid fa-record-vinyl"></i> START RECORDING'; }
    });
    
    btnStopRec.addEventListener('click', async () => {
        btnStopRec.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Stopping Recording...';
        try {
            const res = await fetch('/api/stop-recording', { method: 'POST' });
            const data = await res.json();
            if(data.success) toast.fire({ icon: 'info', title: 'Recording stopped.' });
            else toast.fire({ icon: 'error', title: data.message });
        } catch(e) { toast.fire({ icon: 'error', title: 'Unable to connect to backend.' }); }
        finally { btnStopRec.innerHTML = '<i class="fa-solid fa-stop"></i> STOP RECORDING'; }
    });

    const btnRecord = document.getElementById('btn-record');
    if (btnRecord) {
        btnRecord.addEventListener('click', () => {
            if (badgeRec.classList.contains('active')) {
                btnStopRec.click();
            } else {
                btnStartRec.click();
            }
        });
    }

    // ----- SESSIONS VIEW -----
    document.getElementById('btn-refresh-sessions').addEventListener('click', () => loadSessions(1));
    
    let currentPage = 1;
    const limit = 15;
    
    document.getElementById('btn-prev-page').addEventListener('click', () => {
        if(currentPage > 1) loadSessions(currentPage - 1);
    });
    
    document.getElementById('btn-next-page').addEventListener('click', () => {
        loadSessions(currentPage + 1);
    });

    document.getElementById('btn-close-details').addEventListener('click', () => {
        document.getElementById('session-details').style.display = 'none';
    });

    async function loadSessions(page = 1) {
        currentPage = page;
        const tbody = document.getElementById('sessions-tbody');
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Loading data...</td></tr>';
        
        try {
            const res = await fetch(`/api/sessions?page=${page}&limit=${limit}`);
            const data = await res.json();
            if(data.success && data.data.length > 0) {
                tbody.innerHTML = data.data.map(session => `
                    <tr style="cursor: pointer;" onclick="loadSessionDetails(${session.id})">
                        <td>#${session.id}</td>
                        <td>${session.input_type || 'Unknown'}</td>
                        <td title="${session.source_name}">${session.source_name ? session.source_name.substring(0, 15) : 'N/A'}...</td>
                        <td>${session.started_at ? new Date(session.started_at).toLocaleString() : 'N/A'}</td>
                        <td><span class="status-badge ${session.status}">${session.status}</span></td>
                        <td>${session.average_fps ? session.average_fps.toFixed(1) : '0'}</td>
                        <td>${session.total_detections}</td>
                    </tr>
                `).join('');
                
                document.getElementById('page-indicator').innerText = `Page ${data.pagination.page} of ${data.pagination.pages}`;
                document.getElementById('btn-prev-page').disabled = data.pagination.page <= 1;
                document.getElementById('btn-next-page').disabled = data.pagination.page >= data.pagination.pages;
                
            } else {
                tbody.innerHTML = '<tr><td colspan="7" class="empty-list">No processing sessions found.</td></tr>';
                document.getElementById('page-indicator').innerText = `Page 1`;
                document.getElementById('btn-prev-page').disabled = true;
                document.getElementById('btn-next-page').disabled = true;
            }
        } catch(e) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-list">Unable to connect to backend.</td></tr>';
        }
    }

    window.loadSessionDetails = async function(sessionId) {
        const detailPane = document.getElementById('session-details');
        const detailId = document.getElementById('detail-id');
        const detailTbody = document.getElementById('detail-tbody');
        
        detailPane.style.display = 'block';
        detailId.innerText = '#' + sessionId;
        detailTbody.innerHTML = '<tr><td colspan="5" class="text-center"><i class="fa-solid fa-spinner fa-spin"></i> Loading...</td></tr>';
        
        // Reset modal fields
        document.getElementById('det-modal-input').innerText = 'Loading...';
        document.getElementById('det-modal-source').innerText = 'Loading...';
        document.getElementById('det-modal-start').innerText = 'Loading...';
        document.getElementById('det-modal-end').innerText = 'Loading...';
        document.getElementById('det-modal-status').innerText = 'Loading...';
        document.getElementById('det-modal-total').innerText = 'Loading...';
        document.getElementById('det-modal-tracked').innerText = 'Loading...';
        document.getElementById('det-modal-conf').innerText = 'Loading...';
        document.getElementById('det-modal-fps').innerText = 'Loading...';
        document.getElementById('det-modal-duration').innerText = 'Loading...';
        document.getElementById('modal-downloads').innerHTML = '';
        
        detailPane.scrollIntoView({ behavior: 'smooth' });
        
        try {
            const res = await fetch('/api/session/' + sessionId);
            const responseData = await res.json();
            
            if(responseData.success) {
                const data = responseData.data;
                
                // Populate stats
                document.getElementById('det-modal-input').innerText = data.input_type || 'N/A';
                document.getElementById('det-modal-source').innerText = data.source_name || 'N/A';
                document.getElementById('det-modal-start').innerText = data.started_at ? new Date(data.started_at).toLocaleString() : 'N/A';
                document.getElementById('det-modal-end').innerText = data.completed_at ? new Date(data.completed_at).toLocaleString() : 'Running';
                
                const badgeClass = data.status === 'completed' ? 'completed' : (data.status === 'running' ? 'running' : 'stopped');
                document.getElementById('det-modal-status').innerHTML = `<span class="status-badge ${badgeClass}">${data.status}</span>`;
                
                document.getElementById('det-modal-total').innerText = data.total_detections || 0;
                document.getElementById('det-modal-tracked').innerText = data.total_tracked_objects || 0;
                document.getElementById('det-modal-conf').innerText = data.average_confidence ? data.average_confidence.toFixed(1) + '%' : '0%';
                document.getElementById('det-modal-fps').innerText = data.average_fps ? data.average_fps.toFixed(1) : '0';
                document.getElementById('det-modal-duration').innerText = data.processing_time ? data.processing_time.toFixed(1) + 's' : '0s';
                
                // Add Download and Delete buttons
                let downloadHtml = '';
                if(data.output_video) {
                    downloadHtml += `<a href="/api/session/${sessionId}/output" target="_blank" class="btn primary" style="text-decoration: none;"><i class="fa-solid fa-download"></i> DOWNLOAD OUTPUT VIDEO</a>`;
                }
                if(data.screenshot_path) {
                    downloadHtml += `<a href="/api/session/${sessionId}/screenshot" target="_blank" class="btn outline" style="text-decoration: none; margin-left: 10px;"><i class="fa-solid fa-image"></i> DOWNLOAD SCREENSHOT</a>`;
                }
                downloadHtml += `<button onclick="deleteSession(${sessionId})" class="btn danger" style="margin-left: 10px;"><i class="fa-solid fa-trash"></i> DELETE SESSION</button>`;
                
                document.getElementById('modal-downloads').innerHTML = downloadHtml;
                
                // Populate detections table and calculate class distribution
                let classCounts = {};
                
                if(data.detections && data.detections.length > 0) {
                    detailTbody.innerHTML = data.detections.map(det => {
                        classCounts[det.object_class] = (classCounts[det.object_class] || 0) + 1;
                        return `
                            <tr>
                                <td>${det.tracking_id}</td>
                                <td>${det.object_class}</td>
                                <td class="text-success">${det.confidence.toFixed(1)}%</td>
                                <td>${det.frame_number}</td>
                                <td>${new Date(det.timestamp).toLocaleTimeString()}</td>
                            </tr>
                        `;
                    }).join('');
                    
                    // Populate class distribution container
                    let distributionHtml = Object.entries(classCounts).map(([cls, count]) => `<span style="background: var(--primary); color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: bold;">${cls}: ${count}</span>`).join('');
                    document.getElementById('class-distribution-content').innerHTML = distributionHtml;
                    document.getElementById('class-distribution-container').style.display = 'block';
                    
                } else {
                    detailTbody.innerHTML = '<tr><td colspan="5" class="empty-list">No objects found in this session.</td></tr>';
                    document.getElementById('class-distribution-container').style.display = 'none';
                }
            } else {
                detailTbody.innerHTML = '<tr><td colspan="5" class="empty-list text-danger">Failed to load details.</td></tr>';
            }
        } catch (e) {
            detailTbody.innerHTML = '<tr><td colspan="5" class="empty-list text-danger">Failed to connect to backend.</td></tr>';
        }
    };

    window.deleteSession = async function(sessionId) {
        if(!confirm("Are you sure you want to delete this session? This will remove metadata and associated output files permanently.")) return;
        
        try {
            const res = await fetch('/api/session/' + sessionId, { method: 'DELETE' });
            const data = await res.json();
            if(data.success) {
                toast.fire({ icon: 'success', title: 'Session deleted successfully.' });
                document.getElementById('session-details').style.display = 'none';
                loadSessions(currentPage);
            } else {
                toast.fire({ icon: 'error', title: data.message });
            }
        } catch(e) {
            toast.fire({ icon: 'error', title: 'Unable to connect to backend.' });
        }
    };

    // ----- SETTINGS VIEW -----
    const confSlider = document.getElementById('set-conf');
    const confVal = document.getElementById('conf-val');
    if(confSlider) {
        confSlider.addEventListener('input', (e) => confVal.innerText = e.target.value);
    }

    const navSettings = document.getElementById('nav-settings');
    if(navSettings) {
        navSettings.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/settings');
                const responseData = await res.json();
                if(responseData.success) {
                    const data = responseData.data;
                    document.getElementById('set-camera').value = data.video_source;
                    document.getElementById('set-conf').value = data.confidence_threshold;
                    if(confVal) confVal.innerText = data.confidence_threshold;
                    document.getElementById('set-imgsz').value = data.image_size;
                    document.getElementById('set-device').value = data.device;
                }
            } catch (e) { console.error("Failed to load settings"); }
        });
    }

    document.getElementById('btn-save-settings').addEventListener('click', async () => {
        const btn = document.getElementById('btn-save-settings');
        const ogText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> SAVING...';
        btn.disabled = true;
        
        try {
            const payload = {
                video_source: document.getElementById('set-camera').value,
                confidence_threshold: parseFloat(document.getElementById('set-conf').value),
                image_size: parseInt(document.getElementById('set-imgsz').value),
                device: document.getElementById('set-device').value
            };
            
            const res = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if(data.success) toast.fire({ icon: 'success', title: 'Settings saved successfully.' });
            else toast.fire({ icon: 'error', title: data.message });
        } catch(e) {
            toast.fire({ icon: 'error', title: 'Failed to save settings.' });
        } finally {
            btn.innerHTML = ogText;
            btn.disabled = false;
        }
    });

    // Init
    startPolling();
});
