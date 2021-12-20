new Vue({
    el: '#app',
    data() {
        return {
            show_table : false,
            files : {
                eye : null,
                gill : null,
                skin : null
            },
            detect_result : {
                eye : {
                    prediction: "", 
                    target_param: "", 
                    accuration: ""
                },
                gill : {
                    prediction: "", 
                    target_param: "", 
                    accuration: ""
                },
                skin : {
                    prediction: "", 
                    target_param: "", 
                    accuration: ""
                },
            },
            is_online : true,
            is_loading : false,
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
        //window.history.pushState({ noBackExitsApp: true }, '')
        //window.addEventListener('popstate', this.backPress)
        this.setCurrentHost()
    },
    mounted () {
        window.$('.dropdown-trigger').dropdown()
        window.$('.modal').modal({opacity:0.05,dismissible: false,preventScrolling:false})
        window.$('.sidenav').sidenav()

    },
    computed : {
        getPageName(){
            let param = new URLSearchParams(window.location.search)
            let name = param.get('page')
            return name ? name : "main-page"
        }
    },
    methods : {
        uploadImage(param){
            let formData = new FormData();
            formData.append('file', this.files[param]);
            axios.post(this.baseUrl() + 'detect/process/' + param, formData, {
                headers: {
                'Content-Type': 'multipart/form-data'
                }
            }).then(response => {
                if (response.data.error != null){
                    return
                }
                this.detect_result[response.data.target_param] = response.data
                this.show_table = true

            })
            .catch(errors => {
                console.log(errors)
            }) 
        },
        onFileChange(e,param) {
            let fs = e.target.files || e.dataTransfer.files
            if (!fs.length) return
            this.files[param] = fs[0]
        },
        switchPage(name){
            if ('URLSearchParams' in window) {
                var searchParams = new URLSearchParams(window.location.search);
                searchParams.set('page', name);
                window.location.search = searchParams.toString();
            }
        },
        newPage(name){
            if ('URLSearchParams' in window) {
                var searchParams = new URLSearchParams(window.location.search);
                searchParams.set('page', name);
                window.open("?" + searchParams.toString(), '_blank')
            }
        },
        switchLang(lang){
            if ('URLSearchParams' in window) {
                var searchParams = new URLSearchParams(window.location.search);
                searchParams.set('lang', lang);
                window.location.search = searchParams.toString();
            }
        },
        langCheck(lang){
            let def = "ind"
            let param = new URLSearchParams(window.location.search)
            let name = param.get('lang')
            return name ? (name == lang) : (def == lang)
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
            return this.host.protocol.concat(this.host.name + ":" + this.host.port + "/")
        }
    }
})