new Vue({
    el: '#app',
    data() {
        return {
            is_online : true,
            result : {
                course_id : 0,
                user_id : 0,
                total_answered : 0,
                total_correct : 0
            },
            course : {
                id: 0,
                name: "",
                description: "",
                image_url: "",
                total_exam: 0,
                created_by: 0
            },
            host : {
                name : "",
                protocol : "",
                port : ""
            }
        }
    },
    created(){
        window.addEventListener('offline', () => { this.is_online = false })
        window.addEventListener('online', () => { this.is_online = true })
        window.history.pushState({ noBackExitsApp: true }, '')
        window.addEventListener('popstate', this.backPress )
        this.setCurrentHost()
    },
    mounted(){
        this.loadSession()
    },
    methods : {
        loadCourse(course_id){
            axios
            .post(this.baseUrl() + '/api/course/one.php', {id : course_id})
            .then(response => {
                if (response.data.error != null || response.data.data == null){
                    return
                }
                this.course = response.data.data
                this.loadResult(this.course.id)
            })
            .catch(errors => {
                console.log(errors)
            }) 
        },
        loadResult(course_id){

            if (!window.localStorage.getItem('session')) {
                return;
            }

            let user = JSON.parse(window.localStorage.getItem('session'))

            let data = {
                course_id : course_id,
                user_id : user.id,
                total_answered : 0,
                total_correct : 0
            }

            axios
                .post(this.baseUrl() + '/api/exam_result/result.php',data)
                .then(response => {
                    if (response.data.error != null || response.data.data == null){
                        return
                    }
                    this.result = response.data.data
                })
                .catch(errors => {
                    console.log(errors)
                }) 
  
        },
        reset(course_id){
            if (!window.localStorage.getItem('session')) {
                return;
            }

            let user = JSON.parse(window.localStorage.getItem('session'))

            let data = {
                course_id : course_id,
                user_id : user.id
            }

            axios
                .post(this.baseUrl() + '/api/exam_progress/reset.php',data)
                .then(response => {
                    if (response.data.error != null){
                        return
                    }
                    window.location.reload();
                })
                .catch(errors => {
                    console.log(errors)
                }) 
        },
        loadSession(){
            if (!window.localStorage.getItem('session')) {
                window.location = this.baseUrl() + "/index.html"
                return;
            }

            let param = new URLSearchParams(window.location.search)
            let course_id = param.get('course_id') + "";
    
            this.loadCourse(course_id)
        },
        backPress(){
            if (event.state && event.state.noBackExitsApp) {
                window.history.pushState({ noBackExitsApp: true }, '')
            }
        },
        setCurrentHost(){
            this.host.name = window.location.hostname
            this.host.port = location.port
            this.host.protocol = location.protocol.concat("//")
        },
        baseUrl(){
            return this.host.protocol.concat(this.host.name + ":" + this.host.port)
        }
    }
})
