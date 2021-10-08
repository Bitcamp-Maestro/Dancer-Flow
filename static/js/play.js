class PlayMain {
    constructor(navigator, msg_handler, pid) {
        this.color_frame = document.getElementById('user-canvas-frame')
        this.canvas = document.getElementById('userCanvas'),
        this.context = this.canvas.getContext('2d'),
        this.video = document.getElementById('userVideo'),
        this.play_video = document.getElementById('playVideo'),
        this.playCanvas = document.getElementById('playCanvas'),
        // this.playContext = this.playCanvas.getContext('2d'),
        this.navigator = navigator
        this.navigator.getMedia = navigator.mediaDevices.getUserMedia || navigator.mediaDevices.webkitGetUserMedia || navigator.mediaDevices.mozGetuserMedia || navigator.mediaDevices.msGetUserMedia;
        this.rec = null
        this.fps = 30
        this.loopID = null
        this.score = 0
       
        this.msg_handler = msg_handler
        this.config = {
            pid: pid,
            id: this.msg_handler.clientID,
            start_date: Date.now()
        }
        this.URL = this.msg_handler.URL
    }
    start() {
        this.init_handler()
        this.video.addEventListener('play', e => {
            console.log('play')
            this.draw();
            this.record();
        }, false);
        if(this.video.getAttribute('data-play-mode') !== 'upload'){
            this.initCaptureVideo(this.video);
        }else{
            // this.video.play()
            // this.play_video.play()
        }

        window.onresize = this.resizeCanvas.bind(this);
        this.resizeCanvas.bind(this)()
    }

    init_handler(){
        this.msg_handler.setReceiveCallBack(data=>{
            switch (data.type) {
                case 'message':
                    break;
                case 'update_score':
                    this.updateScore(data.score)
                    break
            }
        })
        console.log(this.msg_handler.receivedCallBack)
    }

    initCaptureVideo(video) {
        this.navigator.mediaDevices
            .getUserMedia({audio: false, video: true})
            .then(gotStream)
            .catch(error => console.error(error));

        function gotStream(stream) {
            // video.src = window.URL.createObjectURL(stream);
            video.srcObject = stream;
            video.play();
        }
    }

    resizeCanvas() {
        console.log('resizing')
        let width = parseInt(window.innerWidth * 0.5);
        let height = parseInt(window.innerHeight * 0.8);

        this.canvas.width = width;
        this.canvas.height = height;

        // this.playCanvas.width = width;
        // this.playCanvas.height = height;
    }

    draw() {        

        this.context.save()
        
        // mirror mode 
        this.context.scale(-1, 1)
        this.context.translate(-this.canvas.width, 0)

        // user display
        this.context.drawImage(this.video, 0,0, this.video.videoWidth*2, this.video.videoHeight, this.canvas.width/2, 0, this.canvas.width, this.canvas.height);
        
        this.context.restore()

        // model diaplay
        this.context.drawImage(this.play_video, 0, 0, this.play_video.videoWidth*2, this.play_video.videoHeight, this.canvas.width/2, 0, this.canvas.width, this.canvas.height);

        //text
        this.context.font = `${0.0025*this.canvas.width}rem serif`;
        this.context.strokeStyle= 'blue'
        this.context.strokeText('USER DISPLAY', 20, 50);
        
        this.context.font = `${0.0025*this.canvas.width}rem serif`;
        this.context.strokeText('PLAY DISPLAY', this.canvas.width/2+10, 50);
        
        this.context.font = `${0.002*this.canvas.width}rem serif`;
        this.context.strokeText('Score', 20, this.canvas.height - 100);
        
        this.context.font = `${0.0025*this.canvas.width}rem serif`;
        this.context.strokeText(this.score, 20, this.canvas.height - 50);

        this.loopID = requestAnimationFrame(this.draw.bind(this))
    }
    updateScore(score) {
        this.score += score
        console.log(this.score)
        this.context.font = `${0.0025*this.canvas.width}rem serif`;
        this.context.strokeStyle= 'blue'
        this.context.strokeText(this.score, 20, this.canvas.height - 50);
    
        this.color_frame.classList.remove('score-bad')
        this.color_frame.classList.remove('score-good')
        this.color_frame.classList.remove('score-perfect')

        if(score > 300){
            this.color_frame.classList.add('score-perfect')
        }else if(score > 100){
            this.color_frame.classList.add('score-good')
        }else{
            this.color_frame.classList.add('score-bad')
        }
    }

    record() {
        const chunks = [];
        const stream = this.canvas.captureStream();
        this.rec = new MediaRecorder(stream);

        this.rec.ondataavailable = e => {
            chunks.push(e.data)
            // const data_chunk = new FormData()
            // data_chunk.append('USER_VIDEO_CHUNK', e.data)
            // this.msg_handler.sendMessage('user-chunk', data_chunk)
            // this.msg_handler.sendMessage('play-chunk', )

        };

        this.rec.onstop = e => {
            cancelAnimationFrame(this.loopID)
            this.msg_handler.close(this.config.pid)
            let video_title = this.video.getAttribute('data-title') + `_playvideo.mp4`
            this.exportVid(new Blob(chunks, {type: 'video/mp4'}), video_title)
            
            const play_data = new FormData()
            const file = new File(chunks, video_title, {'type':'video/mp4'})
            play_data.append('video', file, file.name)
            play_data.append('score', this.score)
            play_data.append('datetime', new Date(Date.now()).toString())
            this.msg_handler.sendResult('http://127.0.0.1:8000/play/?pid=' + this.config.pid, play_data)
        };

        this.play_video.addEventListener('ended', e => {
            this.rec.stop()
            this.endGame() 
        })

        this.rec.start();

    }
    exportVid(blob, title) {
        const video_preview = document.querySelector('#play-video-preview')     
        const line = document.querySelectorAll('.button-line')[0]
        const vid = document.createElement('video');
        const a = document.createElement('a');
        
        vid.src = URL.createObjectURL(blob);
        vid.controls = true;
        vid.classList.add('user_video')

        a.download = title;
        a.href = vid.src;
        
        const btn = document.createElement('button')
        btn.className = 'w-btn w-btn-gra1'
        btn.textContent = 'Download Play Video'

        a.appendChild(btn)
        line.appendChild(a);
        video_preview.appendChild(vid);

        line.classList.remove('content-hide')
        line.classList.add('content-visible')
        
        return vid
    }
    endGame(){
        const share_page = document.querySelector('#result-share')
        const play_content = document.querySelector('#play-content')
  
        share_page.classList.remove('content-hide')
        share_page.classList.add('content-visible')
        play_content.classList.remove('content-visible')
        play_content.classList.add('content-hide')

        setTimeout(this.redirectToShare, 1000)
    }
    redirectToShare(){
        window.location = (""+window.location).replace(/#[A-Za-z0-9_]*$/,'')+"#result-share"        
    }
}

class MessageHandler {
    constructor(URL, pid=null) {
        this.clientID = "client 1"
        this.URL = URL
        this.socket = new WebSocket(this.URL)
        this.receivedCallBack = null
        this.init()
    }
    init() {
        this.socket.onopen = e => {
            this.sendMessage('check', 'connected with client : ' + this.clientID)
        }
        this.socket.onmessage = e => {
            const data = JSON.parse(e.data)
            try{
                this.receivedCallBack(data)
            }catch(error){
                console.log(error)
            }
        }
        this.socket.onclose = e=>{
            this.socket.close()
            console.log('disconnected')
        }
    }
    sendMessage(type, msg) {
        this.socket.send(JSON.stringify({
            'type' : type,
            'message': msg
        }))
    }
    setReceiveCallBack(callback){
        this.receivedCallBack = callback
    }
    close(pid=null) {
        this.socket.send(JSON.stringify({
            'type' : 'close',
            'pid' : pid,
            'message': 'close',
        }))
        this.socket.close()
    }
    makeMessage(func) {
        func()
    }
    async sendResult(URL, datas) {
        const request = new Request(URL + '', {
            headers: {
                'X-CSRFToken': this.getCookie("csrftoken")
            }
        })
        let res = await fetch(request, {
            method: 'POST',
            mode: 'same-origin',
            body: datas
        })
        return res
    }

    getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

function main() {
    const pid = document.querySelector('#userVideo').getAttribute('data-pid')
    let msg_handler = new MessageHandler('ws://127.0.0.1:8000/ws/play/' + pid)
    new PlayMain(navigator, msg_handler, pid).start()
}
main()