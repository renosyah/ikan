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
            img_size_w : 28,
            img_size_h : 28,
            images : {
                eye : "./img/upload_image.png",
                gill : "./img/upload_image.png",
                skin : "./img/upload_image.png",
            },
            detect_result : {
                eye : {
                    prediction: "", 
                    target_param: "", 
                    accuration: "",
                    label : ""
                },
                gill : {
                    prediction: "", 
                    target_param: "", 
                    accuration: "",
                    label : ""
                },
                skin : {
                    prediction: "", 
                    target_param: "", 
                    accuration: "",
                    label : ""
                },
            },
            training_result : {
                eye : {
                    training_model_exist : false
                },
                gill : {
                    training_model_exist : false
                },
                skin : {
                    training_model_exist : false
                }
            },
            result : "",
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
        //this.loadSetting()
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
        uploadImage(param){
            if (!this.training_result[param].training_model_exist){
                return
            }

            this.is_loading = true
            let formData = new FormData();
            formData.append('file', this.files[param])
            formData.append('img_size_w', this.img_size_w)
            formData.append('img_size_h', this.img_size_h)
            axios.post(this.baseUrl() + 'detect/process/' + param, formData, {
                headers: {
                'Content-Type': 'multipart/form-data'
                }
            }).then(response => {
                this.is_loading = false
                if (response.data.error != null){
                    return
                }
                this.detect_result[response.data.target_param] = response.data
                this.show_table = true
                this.result = this.getMostFreq()
                $('html,body').animate({scrollTop: document.body.scrollHeight},"slow");
            })
            .catch(errors => {
                console.log(errors)
            }) 
        },
        onFileChange(e,param) {
            let fs = e.target.files || e.dataTransfer.files
            if (!fs.length) return
            this.files[param] = fs[0]
            this.createImage(param, this.files[param])
            this.uploadImage(param)
        },
        createImage(param,file) {
            let reader = new FileReader()
            let vm = this
            reader.onload = function(e) {
                vm.images[param] = e.target.result
            }
            reader.readAsDataURL(file)
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
        getStore(){
            return [
                [this.detect_result.gill.prediction, this.detect_result.gill.label, 35.0],
                [this.detect_result.skin.prediction, this.detect_result.skin.label, 35.0],
                [this.detect_result.eye.prediction, this.detect_result.eye.label, 30.0]
            ]
        },
        getMostFreq(){
            let store = this.getStore()
            let result = ""
            let pools = {"S" : 0.0, "KS" : 0.0, "B" : 0.0}
            let is_ok = true

            store.forEach((value, index) => {
                if (value[1] != ""){
                    pools[value[1]] += value[2]
                }
            });

            console.log(pools)

            for (let i=0;i<store.lengthl;i++){
                if (store[i][1] == ""){
                    is_ok = false
                    break
                }
            }

            if (!is_ok){
                return "-"
            }

            if (pools["S"] > pools["KS"] && pools["S"] > pools["B"]){
                result = "Segar"
            } else if (pools["KS"] > pools["B"] && pools["KS"] > pools["S"]){
                result = "Kurang Segar"
            } else if (pools["B"] > pools["S"] && pools["B"] > pools["KS"]){
                result = "Busuk"
            } else {
                result = "Error"
            }


            return result
        },
        loadSetting(){
            if (window.localStorage && window.localStorage.getItem('training_setting')) {
                let setting = JSON.parse(window.localStorage.getItem('training_setting'))
                this.img_size_w = setting.img_size_w
                this.img_size_h = setting.img_size_h
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