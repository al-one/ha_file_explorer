(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d2248b2"],{e11a:function(t,e,a){"use strict";a.r(e);var n=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-dialog",{attrs:{width:"500"},model:{value:t.dialog,callback:function(e){t.dialog=e},expression:"dialog"}},[a("v-card",[a("v-card-title",[t._v(" 新建文件 ")]),a("v-card-text",[a("v-form",{on:{submit:function(e){return e.preventDefault(),t.saveClick.apply(null,arguments)}}},[a("v-text-field",{attrs:{label:"文件名",autofocus:!0},model:{value:t.name,callback:function(e){t.name="string"===typeof e?e.trim():e},expression:"name"}})],1),a("span",{staticClass:"red--text"},[t._v(" 注意：新建文件会覆盖已有文件 ")])],1),a("v-divider"),a("v-card-actions",[a("v-spacer"),a("v-btn",{attrs:{color:"primary",text:""},on:{click:t.saveClick}},[t._v(" 保存 ")])],1)],1)],1)},i=[],o=a("5530"),c=(a("b0c0"),a("5880")),l={data:function(){return{dialog:!1,name:""}},computed:Object(c["mapGetters"])(["getFilePath"]),methods:Object(o["a"])(Object(o["a"])({},Object(c["mapActions"])(["operationFile"])),{},{show:function(){this.name="",this.dialog=!0},saveClick:function(){var t=this,e=this.name;if(!e)return this.$toast("请输入名称");this.operationFile({type:"new-file",name:e}).then((function(e){var a=e.code;0===a&&(t.dialog=!1)}))}})},r=l,s=a("2877"),u=Object(s["a"])(r,n,i,!1,null,null,null);e["default"]=u.exports}}]);