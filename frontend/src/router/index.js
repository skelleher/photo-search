import Vue from 'vue'
import Router from 'vue-router'
import main from '@/components/main'
import about from "@/components/about"
import vue_links from "@/components/vue_links"
import not_found from "@/components/not_found"

Vue.use(Router)

export default new Router({
  mode: 'history',
  
  routes: [
    { path: '/', component: main },
    { path: '/about', component: about },
    { path: '*', component: not_found }
  ]
})
