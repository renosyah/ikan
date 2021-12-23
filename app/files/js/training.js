new Vue({
    el: '#app',
    data() {
        return {
            show_table : false,
            query : {
                img_size_w : 28,
                img_size_h : 28,
                hidden_layer : 100,
                max_training_example : 400,
                max_training_test : 300,
                maxiter : 100
            },
            training_result : {
                eye : {
                    total_dataset: "",
                    precision: "", 
                    target_param: "", 
                    test_accuration: "", 
                    training_accuration: "",
                    training_model_exist : false
                },
                gill : {
                    total_dataset: "",
                    precision: "", 
                    target_param: "", 
                    test_accuration: "", 
                    training_accuration: "",
                    training_model_exist : false
                },
                skin : {
                    total_dataset: "",
                    precision: "", 
                    target_param: "", 
                    test_accuration: "", 
                    training_accuration: "",
                    training_model_exist : false
                }
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
        this.loadSetting()
    },
    mounted () {
        window.$('.dropdown-trigger').dropdown()
        window.$('.modal').modal({opacity:0.05,dismissible: false,preventScrolling:false})
        window.$('.sidenav').sidenav()
        this.checkTrainingModelStatus()

    },
    computed : {
        getPageName(){
            let param = new URLSearchParams(window.location.search)
            let name = param.get('page')
            return name ? name : "main-page"
        }
    },
    methods : {
        performTraining(param){
            this.is_loading = true
            axios({
                method: 'post',
                url:  this.baseUrl() + "training/perform/" + param,
                data: this.query
            }).then(response => {
                    this.is_loading = false
                    if (response.data.status == 404) {
                        return
                    }

                    this.training_result[response.data.target_param].total_dataset = response.data.total_dataset
                    this.training_result[response.data.target_param].precision = response.data.precision
                    this.training_result[response.data.target_param].target_param = response.data.target_param 
                    this.training_result[response.data.target_param].test_accuration = response.data.test_accuration
                    this.training_result[response.data.target_param].training_accuration = response.data.training_accuration
                    this.training_result[response.data.target_param].training_model_exist = true

                    this.show_table = true
                    this.checkTrainingModelStatus()
                    this.saveSetting()
                    $('html,body').animate({scrollTop: document.body.scrollHeight},"slow");

                })
                .catch(e => {
                    console.log(e)
                    this.is_loading = false
                })
        },
        checkTrainingModel(param){
            this.is_loading = true
            axios({
                method: 'post',
                url:  this.baseUrl() + "training/" + param,
                data: {}
            }).then(response => {
                    this.is_loading = false
                    if (response.data.status == 404) {
                        return
                    }
                    this.training_result[param].training_model_exist = response.data.is_exist
                })
                .catch(e => {
                    console.log(e)
                    this.is_loading = false
                })
        },
        checkTrainingModelStatus(){
            this.checkTrainingModel('eye')
            this.checkTrainingModel('gill')
            this.checkTrainingModel('skin')
        },
        saveSetting(){
            if (window.localStorage) {
                window.localStorage.setItem('training_setting', JSON.stringify(this.query))
            }
        },
        loadSetting(){
            if (window.localStorage && window.localStorage.getItem('training_setting')) {
                this.query = JSON.parse(window.localStorage.getItem('training_setting'))
            }
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