document.addEventListener('DOMContentLoaded', function() {
    // ==================== 通用功能 ====================
    // 初始化Bootstrap工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // 自动关闭警告消息
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // ==================== 表单处理 ====================
    // 表单提交按钮状态管理
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 处理中...';
            }
        });
    });

    // ==================== 视频功能 ====================
    // 初始化所有视频播放器
    document.querySelectorAll('.video-js').forEach(videoEl => {
        const videoId = videoEl.id.replace('my-video-', '');
        const sources = Array.from(videoEl.querySelectorAll('source')).map(source => ({
            src: source.src,
            type: source.type,
            label: source.getAttribute('label')
        }));

        // 检查浏览器是否支持HLS原生播放
        const canPlayHls = videoEl.canPlayType('application/vnd.apple.mpegurl');
        
        // 如果浏览器不支持原生HLS，使用hls.js
        if (!canPlayHls && Hls.isSupported()) {
            const hls = new Hls();
            const firstSource = sources[0];
            
            hls.loadSource(firstSource.src);
            hls.attachMedia(videoEl);
            hls.on(Hls.Events.MANIFEST_PARSED, function() {
                // 初始化video.js播放器
                const player = videojs(videoEl, {
                    controls: true,
                    autoplay: false,
                    preload: 'auto',
                    responsive: true,
                    fluid: true,
                    playbackRates: [0.5, 1, 1.5, 2]
                });
                
                // 质量选择器
                const selector = document.getElementById(`quality-selector-${videoId}`);
                if (selector) {
                    selector.addEventListener('change', function() {
                        const selectedOption = this.options[this.selectedIndex];
                        const currentTime = player.currentTime();
                        hls.loadSource(selectedOption.dataset.src);
                        player.currentTime(currentTime);
                        player.play()
                    });
                }
            });
        } else {
            // 浏览器支持原生HLS，直接使用video.js
            const player = videojs(videoEl, {
                controls: true,
                autoplay: false,
                preload: 'auto',
                responsive: true,
                fluid: true,
                playbackRates: [0.5, 1, 1.5, 2]
            });

            // 质量选择器
            const selector = document.getElementById(`quality-selector-${videoId}`);
            if (selector) {
                selector.addEventListener('change', function() {
                    const selectedOption = this.options[this.selectedIndex];
                    const currentTime = player.currentTime();
                    player.src({
                        src: selectedOption.dataset.src,
                        type: 'application/x-mpegURL'
                    });
                    player.currentTime(currentTime);
                    player.play()
                });
            }
        }
    });

    // ==================== 工具函数 ====================
    function getRandomColor() {
        const colors = ['#ffffff', '#ff9999', '#99ff99', '#9999ff', '#ffff99', '#ff99ff', '#99ffff', '#ffcc99'];
        return colors[Math.floor(Math.random() * colors.length)];
    }
});