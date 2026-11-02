var yn=Object.defineProperty;var _n=(s,t,e)=>t in s?yn(s,t,{enumerable:!0,configurable:!0,writable:!0,value:e}):s[t]=e;var x=(s,t,e)=>_n(s,typeof t!="symbol"?t+"":t,e);var he=globalThis,de=he.ShadowRoot&&(he.ShadyCSS===void 0||he.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Ne=Symbol(),Rs=new WeakMap,Ht=class{constructor(t,e,r){if(this._$cssResult$=!0,r!==Ne)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(de&&t===void 0){let r=e!==void 0&&e.length===1;r&&(t=Rs.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),r&&Rs.set(e,t))}return t}toString(){return this.cssText}},Os=s=>new Ht(typeof s=="string"?s:s+"",void 0,Ne),A=(s,...t)=>{let e=s.length===1?s[0]:t.reduce((r,n,o)=>r+(i=>{if(i._$cssResult$===!0)return i.cssText;if(typeof i=="number")return i;throw Error("Value passed to 'css' function must be a 'css' function result: "+i+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(n)+s[o+1],s[0]);return new Ht(e,s,Ne)},Ts=(s,t)=>{if(de)s.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let r=document.createElement("style"),n=he.litNonce;n!==void 0&&r.setAttribute("nonce",n),r.textContent=e.cssText,s.appendChild(r)}},Le=de?s=>s:s=>s instanceof CSSStyleSheet?(t=>{let e="";for(let r of t.cssRules)e+=r.cssText;return Os(e)})(s):s;var{is:xn,defineProperty:wn,getOwnPropertyDescriptor:$n,getOwnPropertyNames:Mn,getOwnPropertySymbols:kn,getPrototypeOf:Sn}=Object,tt=globalThis,Ns=tt.trustedTypes,An=Ns?Ns.emptyScript:"",En=tt.reactiveElementPolyfillSupport,jt=(s,t)=>s,De={toAttribute(s,t){switch(t){case Boolean:s=s?An:null;break;case Object:case Array:s=s==null?s:JSON.stringify(s)}return s},fromAttribute(s,t){let e=s;switch(t){case Boolean:e=s!==null;break;case Number:e=s===null?null:Number(s);break;case Object:case Array:try{e=JSON.parse(s)}catch{e=null}}return e}},Ds=(s,t)=>!xn(s,t),Ls={attribute:!0,type:String,converter:De,reflect:!1,useDefault:!1,hasChanged:Ds};Symbol.metadata??(Symbol.metadata=Symbol("metadata")),tt.litPropertyMetadata??(tt.litPropertyMetadata=new WeakMap);var G=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??(this.l=[])).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=Ls){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let r=Symbol(),n=this.getPropertyDescriptor(t,r,e);n!==void 0&&wn(this.prototype,t,n)}}static getPropertyDescriptor(t,e,r){let{get:n,set:o}=$n(this.prototype,t)??{get(){return this[e]},set(i){this[e]=i}};return{get:n,set(i){let a=n?.call(this);o?.call(this,i),this.requestUpdate(t,a,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??Ls}static _$Ei(){if(this.hasOwnProperty(jt("elementProperties")))return;let t=Sn(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(jt("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(jt("properties"))){let e=this.properties,r=[...Mn(e),...kn(e)];for(let n of r)this.createProperty(n,e[n])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[r,n]of e)this.elementProperties.set(r,n)}this._$Eh=new Map;for(let[e,r]of this.elementProperties){let n=this._$Eu(e,r);n!==void 0&&this._$Eh.set(n,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let r=new Set(t.flat(1/0).reverse());for(let n of r)e.unshift(Le(n))}else t!==void 0&&e.push(Le(t));return e}static _$Eu(t,e){let r=e.attribute;return r===!1?void 0:typeof r=="string"?r:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??(this._$EO=new Set)).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let r of e.keys())this.hasOwnProperty(r)&&(t.set(r,this[r]),delete this[r]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Ts(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,r){this._$AK(t,r)}_$ET(t,e){let r=this.constructor.elementProperties.get(t),n=this.constructor._$Eu(t,r);if(n!==void 0&&r.reflect===!0){let o=(r.converter?.toAttribute!==void 0?r.converter:De).toAttribute(e,r.type);this._$Em=t,o==null?this.removeAttribute(n):this.setAttribute(n,o),this._$Em=null}}_$AK(t,e){let r=this.constructor,n=r._$Eh.get(t);if(n!==void 0&&this._$Em!==n){let o=r.getPropertyOptions(n),i=typeof o.converter=="function"?{fromAttribute:o.converter}:o.converter?.fromAttribute!==void 0?o.converter:De;this._$Em=n;let a=i.fromAttribute(e,o.type);this[n]=a??this._$Ej?.get(n)??a,this._$Em=null}}requestUpdate(t,e,r,n=!1,o){if(t!==void 0){let i=this.constructor;if(n===!1&&(o=this[t]),r??(r=i.getPropertyOptions(t)),!((r.hasChanged??Ds)(o,e)||r.useDefault&&r.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(i._$Eu(t,r))))return;this.C(t,e,r)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:r,reflect:n,wrapped:o},i){r&&!(this._$Ej??(this._$Ej=new Map)).has(t)&&(this._$Ej.set(t,i??e??this[t]),o!==!0||i!==void 0)||(this._$AL.has(t)||(this.hasUpdated||r||(e=void 0),this._$AL.set(t,e)),n===!0&&this._$Em!==t&&(this._$Eq??(this._$Eq=new Set)).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??(this.renderRoot=this.createRenderRoot()),this._$Ep){for(let[n,o]of this._$Ep)this[n]=o;this._$Ep=void 0}let r=this.constructor.elementProperties;if(r.size>0)for(let[n,o]of r){let{wrapped:i}=o,a=this[n];i!==!0||this._$AL.has(n)||a===void 0||this.C(n,void 0,o,a)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(r=>r.hostUpdate?.()),this.update(e)):this._$EM()}catch(r){throw t=!1,this._$EM(),r}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&(this._$Eq=this._$Eq.forEach(e=>this._$ET(e,this[e]))),this._$EM()}updated(t){}firstUpdated(t){}};G.elementStyles=[],G.shadowRootOptions={mode:"open"},G[jt("elementProperties")]=new Map,G[jt("finalized")]=new Map,En?.({ReactiveElement:G}),(tt.reactiveElementVersions??(tt.reactiveElementVersions=[])).push("2.1.2");var Ft=globalThis,Is=s=>s,ue=Ft.trustedTypes,Us=ue?ue.createPolicy("lit-html",{createHTML:s=>s}):void 0,Vs="$lit$",et=`lit$${Math.random().toFixed(9).slice(2)}$`,Ws="?"+et,Cn=`<${Ws}>`,mt=document,Vt=()=>mt.createComment(""),Wt=s=>s===null||typeof s!="object"&&typeof s!="function",Fe=Array.isArray,Pn=s=>Fe(s)||typeof s?.[Symbol.iterator]=="function",Ie=`[ 	
\f\r]`,Bt=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,qs=/-->/g,Hs=/>/g,pt=RegExp(`>|${Ie}(?:([^\\s"'>=/]+)(${Ie}*=${Ie}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),js=/'/g,Bs=/"/g,Gs=/^(?:script|style|textarea|title)$/i,Ve=s=>(t,...e)=>({_$litType$:s,strings:t,values:e}),w=Ve(1),ei=Ve(2),si=Ve(3),K=Symbol.for("lit-noChange"),$=Symbol.for("lit-nothing"),Fs=new WeakMap,ft=mt.createTreeWalker(mt,129);function Ks(s,t){if(!Fe(s)||!s.hasOwnProperty("raw"))throw Error("invalid template strings array");return Us!==void 0?Us.createHTML(t):t}var zn=(s,t)=>{let e=s.length-1,r=[],n,o=t===2?"<svg>":t===3?"<math>":"",i=Bt;for(let a=0;a<e;a++){let l=s[a],c,d,h=-1,u=0;for(;u<l.length&&(i.lastIndex=u,d=i.exec(l),d!==null);)u=i.lastIndex,i===Bt?d[1]==="!--"?i=qs:d[1]!==void 0?i=Hs:d[2]!==void 0?(Gs.test(d[2])&&(n=RegExp("</"+d[2],"g")),i=pt):d[3]!==void 0&&(i=pt):i===pt?d[0]===">"?(i=n??Bt,h=-1):d[1]===void 0?h=-2:(h=i.lastIndex-d[2].length,c=d[1],i=d[3]===void 0?pt:d[3]==='"'?Bs:js):i===Bs||i===js?i=pt:i===qs||i===Hs?i=Bt:(i=pt,n=void 0);let p=i===pt&&s[a+1].startsWith("/>")?" ":"";o+=i===Bt?l+Cn:h>=0?(r.push(c),l.slice(0,h)+Vs+l.slice(h)+et+p):l+et+(h===-2?a:p)}return[Ks(s,o+(s[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),r]},Gt=class s{constructor({strings:t,_$litType$:e},r){let n;this.parts=[];let o=0,i=0,a=t.length-1,l=this.parts,[c,d]=zn(t,e);if(this.el=s.createElement(c,r),ft.currentNode=this.el.content,e===2||e===3){let h=this.el.content.firstChild;h.replaceWith(...h.childNodes)}for(;(n=ft.nextNode())!==null&&l.length<a;){if(n.nodeType===1){if(n.hasAttributes())for(let h of n.getAttributeNames())if(h.endsWith(Vs)){let u=d[i++],p=n.getAttribute(h).split(et),m=/([.?@])?(.*)/.exec(u);l.push({type:1,index:o,name:m[2],strings:p,ctor:m[1]==="."?qe:m[1]==="?"?He:m[1]==="@"?je:Ot}),n.removeAttribute(h)}else h.startsWith(et)&&(l.push({type:6,index:o}),n.removeAttribute(h));if(Gs.test(n.tagName)){let h=n.textContent.split(et),u=h.length-1;if(u>0){n.textContent=ue?ue.emptyScript:"";for(let p=0;p<u;p++)n.append(h[p],Vt()),ft.nextNode(),l.push({type:2,index:++o});n.append(h[u],Vt())}}}else if(n.nodeType===8)if(n.data===Ws)l.push({type:2,index:o});else{let h=-1;for(;(h=n.data.indexOf(et,h+1))!==-1;)l.push({type:7,index:o}),h+=et.length-1}o++}}static createElement(t,e){let r=mt.createElement("template");return r.innerHTML=t,r}};function Rt(s,t,e=s,r){if(t===K)return t;let n=r!==void 0?e._$Co?.[r]:e._$Cl,o=Wt(t)?void 0:t._$litDirective$;return n?.constructor!==o&&(n?._$AO?.(!1),o===void 0?n=void 0:(n=new o(s),n._$AT(s,e,r)),r!==void 0?(e._$Co??(e._$Co=[]))[r]=n:e._$Cl=n),n!==void 0&&(t=Rt(s,n._$AS(s,t.values),n,r)),t}var Ue=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:r}=this._$AD,n=(t?.creationScope??mt).importNode(e,!0);ft.currentNode=n;let o=ft.nextNode(),i=0,a=0,l=r[0];for(;l!==void 0;){if(i===l.index){let c;l.type===2?c=new Kt(o,o.nextSibling,this,t):l.type===1?c=new l.ctor(o,l.name,l.strings,this,t):l.type===6&&(c=new Be(o,this,t)),this._$AV.push(c),l=r[++a]}i!==l?.index&&(o=ft.nextNode(),i++)}return ft.currentNode=mt,n}p(t){let e=0;for(let r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(t,r,e),e+=r.strings.length-2):r._$AI(t[e])),e++}},Kt=class s{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,r,n){this.type=2,this._$AH=$,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=r,this.options=n,this._$Cv=n?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Rt(this,t,e),Wt(t)?t===$||t==null||t===""?(this._$AH!==$&&this._$AR(),this._$AH=$):t!==this._$AH&&t!==K&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Pn(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==$&&Wt(this._$AH)?this._$AA.nextSibling.data=t:this.T(mt.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:r}=t,n=typeof r=="number"?this._$AC(t):(r.el===void 0&&(r.el=Gt.createElement(Ks(r.h,r.h[0]),this.options)),r);if(this._$AH?._$AD===n)this._$AH.p(e);else{let o=new Ue(n,this),i=o.u(this.options);o.p(e),this.T(i),this._$AH=o}}_$AC(t){let e=Fs.get(t.strings);return e===void 0&&Fs.set(t.strings,e=new Gt(t)),e}k(t){Fe(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,r,n=0;for(let o of t)n===e.length?e.push(r=new s(this.O(Vt()),this.O(Vt()),this,this.options)):r=e[n],r._$AI(o),n++;n<e.length&&(this._$AR(r&&r._$AB.nextSibling,n),e.length=n)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let r=Is(t).nextSibling;Is(t).remove(),t=r}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},Ot=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,r,n,o){this.type=1,this._$AH=$,this._$AN=void 0,this.element=t,this.name=e,this._$AM=n,this.options=o,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=$}_$AI(t,e=this,r,n){let o=this.strings,i=!1;if(o===void 0)t=Rt(this,t,e,0),i=!Wt(t)||t!==this._$AH&&t!==K,i&&(this._$AH=t);else{let a=t,l,c;for(t=o[0],l=0;l<o.length-1;l++)c=Rt(this,a[r+l],e,l),c===K&&(c=this._$AH[l]),i||(i=!Wt(c)||c!==this._$AH[l]),c===$?t=$:t!==$&&(t+=(c??"")+o[l+1]),this._$AH[l]=c}i&&!n&&this.j(t)}j(t){t===$?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},qe=class extends Ot{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===$?void 0:t}},He=class extends Ot{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==$)}},je=class extends Ot{constructor(t,e,r,n,o){super(t,e,r,n,o),this.type=5}_$AI(t,e=this){if((t=Rt(this,t,e,0)??$)===K)return;let r=this._$AH,n=t===$&&r!==$||t.capture!==r.capture||t.once!==r.once||t.passive!==r.passive,o=t!==$&&(r===$||n);n&&this.element.removeEventListener(this.name,this,r),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},Be=class{constructor(t,e,r){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(t){Rt(this,t)}};var Rn=Ft.litHtmlPolyfillSupport;Rn?.(Gt,Kt),(Ft.litHtmlVersions??(Ft.litHtmlVersions=[])).push("3.3.3");var Ys=(s,t,e)=>{let r=e?.renderBefore??t,n=r._$litPart$;if(n===void 0){let o=e?.renderBefore??null;r._$litPart$=n=new Kt(t.insertBefore(Vt(),o),o,void 0,e??{})}return n._$AI(s),n};var Yt=globalThis,C=class extends G{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var e;let t=super.createRenderRoot();return(e=this.renderOptions).renderBefore??(e.renderBefore=t.firstChild),t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=Ys(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return K}};C._$litElement$=!0,C.finalized=!0,Yt.litElementHydrateSupport?.({LitElement:C});var On=Yt.litElementPolyfillSupport;On?.({LitElement:C});(Yt.litElementVersions??(Yt.litElementVersions=[])).push("4.2.2");var Zs=A`
    /* Generated from shared/tokens.js by scripts/generate/host-tokens.js. */
    /* Do not edit by hand — edit the token tree instead. */

    --font-body: var(--font-body-family, 'Host Grotesk'), var(--font-body-fallback, system-ui, sans-serif);
    --font-label: var(--font-label-family, 'Tomorrow'), var(--font-label-fallback, system-ui, -apple-system, Segoe UI, sans-serif);
    --font-mono: var(--font-mono-family, 'JetBrains Mono'), var(--font-mono-fallback, ui-monospace, monospace);
    --font-quote: var(--font-quote-family, Georgia), var(--font-quote-fallback, serif);
    --font-display: var(--font-display-family, var(--font-body-family, 'Host Grotesk')), var(--font-display-fallback, var(--font-body-fallback, system-ui, sans-serif));
    --font-accent: var(--font-label);

    /* Private mirrors: components read these, consumers override --text-*. */
    --_text-xs: var(--text-xs, 12px);
    --_text-sm: var(--text-sm, 16px);
    --_text-md: var(--text-md, 17px);
    --_text-lg: var(--text-lg, clamp(18px, 1.5vw, 20px));
    --_text-xl: var(--text-xl, clamp(22px, 2.5vw, 26px));
    --_text-2xl: var(--text-2xl, clamp(28px, 3vw, 36px));
    --_text-3xl: var(--text-3xl, clamp(36px, 5vw, 52px));

    --display-xl-size: var(--_text-3xl);
    --display-xl-weight: var(--font-display-weight, 500);
    --display-xl-spacing: -1px;
    --heading-size: var(--_text-xl);
    --heading-weight: var(--font-display-weight, 500);
    --heading-lh: 1.2;
    --body-size: var(--_text-md);
    --body-weight: var(--font-body-weight, 500);
    --body-lh: 1.7;
    --wordmark-size: clamp(20px, 2.5vw, 28px);
    --wordmark-weight: var(--font-display-weight, 500);
    --wordmark-spacing: clamp(8px, 1.2vw, 14px);
    --glyph-lh: 1;
    --ui-size: 14px;
    --ui-lh: 1.4;
    --numeral-size: clamp(24px, 3vw, 36px);
    --numeral-weight: 200;
    --label-size: var(--_text-xs);
    --label-weight: var(--font-label-weight, 600);
    --label-spacing: 2px;
    --section-title-size: var(--label-size);
    --section-title-weight: var(--label-weight);
    --section-title-spacing: var(--label-spacing);
    --ui-accent-size: 16px;
    --ui-accent-weight: var(--font-label-weight, 600);
    --ui-accent-spacing: 0.5px;
    --code-size: 14px;
    --code-lh: 1.8;
    --label-inline-size: 10px;
    --label-inline-spacing: 0.75px;

    /* Spacing */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 40px;
    --space-2xl: 64px;
    --space-3xl: 96px;
    --space-4xl: 128px;

    /* Radii */
    --radius-xs: 2px;
    --radius-sm: 4px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 20px;
    --radius-full: 9999px;

    /* Transitions and motion */
    --transition-fast: var(--duration-fast) var(--ease-standard);
    --transition-base: var(--duration-base) var(--ease-standard);
    --transition-slow: var(--duration-slow) var(--ease-standard);
    --transition-enter: var(--duration-enter) var(--ease-out);
    --transition-exit: var(--duration-exit) var(--ease-in);
    --ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    --ease-in: cubic-bezier(0.7, 0, 0.84, 0);
    --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
    --duration-fast: 120ms;
    --duration-base: 200ms;
    --duration-slow: 400ms;
    --duration-enter: 500ms;
    --duration-exit: 300ms;
    --ease-out-expo: var(--ease-out);
    --ease-in-out: var(--ease-standard);

    /* Z-index */
    --z-base: 0;
    --z-dropdown: 1000;
    --z-tooltip: 1100;
    --z-overlay: 1200;
    --z-modal: 1300;
    --z-toast: 1400;
    --z-max: 9999;

    /* Glow and focus */
    --glow-xs: 0 0 6px rgba(var(--accent-primary-rgb), 0.3);
    --glow-sm: 0 0 8px rgba(var(--accent-primary-rgb), 0.3);
    --glow-md: 0 0 12px rgba(var(--accent-primary-rgb), 0.25);
    --glow-status: 0 0 12px rgba(var(--_status-rgb), var(--glow-status-alpha, 0.15));
    --glow-status-alpha: 0.15;
    --glow-hover: 0 0 12px rgba(var(--accent-primary-rgb), 0.15);
    --focus-ring: 0 0 0 1px rgba(var(--accent-primary-rgb),0.25);
    --focus-glow: 0 0 0 1px rgba(var(--accent-primary-rgb),0.2), 0 0 6px rgba(var(--accent-primary-rgb),0.35), 0 0 16px rgba(var(--accent-primary-rgb),0.2), 0 0 40px rgba(var(--accent-secondary-rgb),0.12);
    --focus-error: 0 0 0 2px var(--surface-base), 0 0 0 4px var(--color-error), 0 0 16px rgba(var(--color-error-rgb), 0.2);
    --focus-inset: inset 0 0 0 2px var(--interactive);
    --focus-thumb: 0 0 8px rgba(var(--interactive-rgb), 0.5), 0 0 20px rgba(var(--interactive-rgb), 0.25);

    /* Decorative presets */
    --gradient-sunset: linear-gradient(135deg, #ff6b6b, #ffa500, #ff4757);
    --gradient-ocean: linear-gradient(135deg, #00d2ff, #3a7bd5, #6dd5fa);
    --orb-close: #ff5f57;
    --orb-minimize: #febc2e;
    --orb-maximize: #28c840;

    /* Lobes of light */
    --lobe-line: linear-gradient(var(--lobe-axis, 90deg), rgba(var(--lobe-rgb, var(--border-default-rgb)), 0), rgba(var(--lobe-rgb, var(--border-default-rgb)), var(--lobe-alpha, 1)), rgba(var(--lobe-rgb, var(--border-default-rgb)), 0));
    --lobe-start: linear-gradient(var(--lobe-axis, 90deg), rgba(var(--lobe-rgb, var(--border-default-rgb)), var(--lobe-alpha, 1)), rgba(var(--lobe-rgb, var(--border-default-rgb)), 0));
    --lobe-end: linear-gradient(var(--lobe-axis, 90deg), rgba(var(--lobe-rgb, var(--border-default-rgb)), 0), rgba(var(--lobe-rgb, var(--border-default-rgb)), var(--lobe-alpha, 1)));
    --lobe-ambient: radial-gradient(var(--lobe-shape, ellipse), rgba(var(--lobe-rgb, var(--border-default-rgb)), var(--lobe-alpha, 0.08)) 0%, rgba(var(--lobe-rgb, var(--border-default-rgb)), 0) var(--lobe-extent, 70%));

    /* Semantic aliases */
    --interactive: var(--accent-primary);
    --interactive-rgb: var(--accent-primary-rgb);
    --interactive-hover: var(--glow-hover);
    --interactive-active: var(--glow-primary);
    --interactive-focus: var(--focus-glow);
    --interactive-focus-ring: var(--focus-ring);
    --interactive-focus-error: var(--focus-error);
    --interactive-focus-inset: var(--focus-inset);
    --interactive-focus-thumb: var(--focus-thumb);
    --interactive-muted: var(--text-ghost);
    --surface-base: var(--bg-deep);
    --surface-primary: var(--bg-surface);
    --surface-raised: var(--bg-card);
    --surface-overlay: var(--bg-elevated);
    --surface-hover: var(--bg-hover);
    --divider: var(--border-subtle);
    --on-accent: var(--surface-base);

    /* Interactive and layout */
    --touch-min: 24px;
    --touch-pad: 4px;
    --max-width: 1120px;
    --max-width-sm: 720px;
    --nav-height: 64px;
    --nav-row-inset: var(--space-sm);
`,Xs=A`
  @media (pointer: coarse) {
    :host {
      --touch-min: 36px;
      --touch-pad: 8px;
    }
  }
`;var yi=A`
  *, *::before, *::after {
    box-sizing: border-box;
  }
`,L=A`
  *, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  /* Neutralise the UA stylesheet for [popover]. PositionController promotes
     floating panels to the top layer, and the UA rules for a popover include
     a solid border, padding, a canvas background and inset:0/margin:auto,
     enough to inflate a measured panel by 14px and to paint a border no
     component asked for. :where() keeps this at zero specificity so it beats
     the UA origin but loses to every rule a component writes for itself. */
  :where([popover]) {
    border: 0;
    padding: 0;
    margin: 0;
    inset: auto;
    width: auto;
    height: auto;
    background: none;
    color: inherit;
    overflow: visible;
  }

  :host {
    transition: opacity var(--transition-fast);

    ${Zs}
  }

  /* The hidden attribute hides, on every component. A component's own
     :host display (block, flex, inline-flex…) outranked the UA's
     [hidden] { display: none }, so hiding an element the platform way did
     nothing: a filtered arc-list-item stayed on screen. :host([hidden]) is
     more specific than any bare :host, so it wins wherever it is declared,
     and it lives here once rather than in every file. */
  :host([hidden]) {
    display: none;
  }

  ${Xs}

  /* Reduced motion, once, for every component that adopts these styles.

     This was copy-pasted verbatim into sixty-nine component files while fifteen
     animating components had no guard at all, which is the usual outcome when
     a cross-cutting rule is a convention rather than a place. Components keep
     their own blocks only for what this cannot express: scroll-behavior,
     animation-play-state, a transform that must be neutralised rather than
     shortened.

     0.01ms rather than "animation: none" on purpose. A component that removes
     itself on animationend (the exiting toast and snackbar both do) would
     wait forever for an event that a canceled animation never fires. A
     duration this short is imperceptible and still completes. */
  @media (prefers-reduced-motion: reduce) {
    :host *,
    :host *::before,
    :host *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
`;var gt=class extends C{constructor(){super(),this.target="#main"}render(){return w`
      <a class="skip-link" href=${this.target} part="base link">
        <slot>Skip to content</slot>
      </a>
    `}};x(gt,"properties",{target:{type:String}}),x(gt,"styles",[L,A`
      :host {
        display: contents;
      }

      .skip-link {
        position: fixed;
        top: var(--space-md);
        left: 50%;
        transform: translateX(-50%) translateY(-200%);
        z-index: var(--z-max);
        background: var(--interactive);
        color: white;
        padding: var(--space-xs) var(--space-lg);
        border-radius: var(--radius-full);
        font-family: var(--font-label);
        font-size: var(--_text-sm);
        font-weight: var(--font-label-weight, 600);
        text-decoration: none;
        transition: transform var(--duration-fast) var(--ease-out-expo);
        white-space: nowrap;
      }

      .skip-link:focus-visible {
        transform: translateX(-50%) translateY(0);
        box-shadow: var(--interactive-focus), 0 0 20px rgba(var(--interactive-rgb), 0.3);
        outline: none;
      }
    `]);customElements.get("arc-skip-link")||customElements.define("arc-skip-link",gt);gt[Symbol.for("tagName")]="arc-skip-link";var Js=A`
  /* ── Primary ── */
  :host([variant="primary"]) .btn,
  :host([variant="primary"]) .btn-slot::slotted(a) {
    background: var(--interactive);
    color: var(--on-accent);
    border-color: var(--interactive);
  }
  :host([variant="primary"]) .btn:hover,
  :host([variant="primary"]) .btn-slot::slotted(a:hover) {
    box-shadow: var(--interactive-active);
  }

  /* ── Secondary ── */
  :host([variant="secondary"]) .btn,
  :host([variant="secondary"]) .btn-slot::slotted(a) {
    background: transparent;
    color: var(--text-primary);
    border-color: var(--border-default);
  }
  :host([variant="secondary"]) .btn:hover,
  :host([variant="secondary"]) .btn-slot::slotted(a:hover) {
    border-color: var(--interactive);
    color: var(--interactive);
    box-shadow: 0 0 20px rgba(var(--interactive-rgb), 0.15);
  }

  /* ── Ghost ── */
  :host([variant="ghost"]) .btn,
  :host([variant="ghost"]) .btn-slot::slotted(a) {
    background: transparent;
    color: var(--text-muted);
    border-color: transparent;
  }
  :host([variant="ghost"]) .btn:hover,
  :host([variant="ghost"]) .btn-slot::slotted(a:hover) {
    color: var(--text-primary);
    background: var(--surface-hover);
  }

  /* ── Focus ── */
  .btn:focus-visible { outline: none; box-shadow: var(--interactive-focus); }
  .btn-slot::slotted(a:focus-visible) { outline: none; box-shadow: var(--interactive-focus); }

  /* ── Disabled ── */
  :host([disabled]) .btn,
  :host([disabled]) .btn-slot::slotted(a) { opacity: 0.5; cursor: not-allowed; pointer-events: none; }
`,Ei=A`
  /* Circular. An icon-only control has no text to give it a reading direction,
     so a square is arbitrary about its corners in a way a circle is not; it
     also separates the bare-glyph controls from the labeled, rectangular ones
     at a glance. This is the shape arc-theme-toggle already had, now applied to
     both rather than to one of them. */
  .btn:not(.btn--has-text),
  .btn-slot::slotted(a) { border-radius: var(--radius-full); }

  .btn:not(.btn--has-text) { aspect-ratio: 1; }

  .btn:not(.btn--has-text),
  .btn-slot::slotted(a) { min-width: var(--touch-min); min-height: var(--touch-min); }

  /* The default arm is keyed on "not the others" so an unrecognized size lands
     on it rather than on no rule at all. See check-enum-fallbacks.js. The
     explicit [size="md"] selector stays so prism can infer the union. */
  :host(:not([size="lg"]):not([size="sm"]):not([size="xs"])) .btn:not(.btn--has-text),
  :host(:not([size="lg"]):not([size="sm"]):not([size="xs"])) .btn-slot::slotted(a),
  :host([size="md"]) .btn:not(.btn--has-text),
  :host([size="md"]) .btn-slot::slotted(a) { width: 36px; height: 36px; }

  :host([size="xs"]) .btn:not(.btn--has-text),
  :host([size="xs"]) .btn-slot::slotted(a) { width: 28px; height: 28px; }

  :host([size="sm"]) .btn:not(.btn--has-text),
  :host([size="sm"]) .btn-slot::slotted(a) { width: 32px; height: 32px; }

  :host([size="lg"]) .btn:not(.btn--has-text),
  :host([size="lg"]) .btn-slot::slotted(a) { width: 44px; height: 44px; }
`;function Tn(s){return s.filter(t=>t.nodeType!==3||t.textContent.trim()!=="")}function Qs(s){let t=Tn(s.assignedNodes({flatten:!0}));return t.length===1&&t[0].nodeType===1&&t[0].localName==="a"}function st(s){let t=()=>{let e=s.renderRoot;if(e?.querySelectorAll)for(let r of e.querySelectorAll("slot"))r.dispatchEvent(new Event("slotchange"))};queueMicrotask(t),typeof document<"u"&&document.readyState==="loading"&&document.addEventListener("DOMContentLoaded",t,{once:!0})}function tr(s,t,e){if(e.some(n=>t.has(n)&&t.get(n)!==void 0)){for(let n=s.parentElement;n;n=n.parentElement)if(typeof n.requestUpdate=="function"){n.requestUpdate();return}}}var We=Symbol("arc-hydrating");function Nn(s,t,e){let r=s.constructor.elementProperties?.get(t),n=r?.attribute===!1?null:typeof r?.attribute=="string"?r.attribute:t.toLowerCase();if(n&&s.hasAttribute(n)){let o=r?.converter?.fromAttribute??r?.converter;if(typeof o=="function")return o(s.getAttribute(n),r.type)}return bt(s,e)}var Ln=new Set(["false","0","off"]);function j(s=!1,{negative:t=null,attribute:e,reflect:r=!0,derived:n=!1,blockedBy:o,nullable:i=!1}={}){if(i&&(s=s===!1?null:s),s&&!t)throw new Error('flag(true) needs a `negative` attribute name \u2014 a true default has no presence-based markup for its false state. e.g. flag(true, { negative: "no-dots" })');return{type:Boolean,reflect:r,...e?{attribute:e}:{},converter:{fromAttribute:a=>a===null?s:!Ln.has(a.toLowerCase()),toAttribute:a=>a?"":null},arc:{kind:"flag",default:s,negative:t,derived:n,blockedBy:o,nullable:i}}}function q(s,{default:t=s[0],attribute:e,reflect:r=!0,derived:n=!1}={}){if(!s?.length)throw new Error("oneOf() needs at least one value");let o=s.every(i=>typeof i=="number");if(!o&&s.some(i=>typeof i=="number"))throw new Error("oneOf() values must be all strings or all numbers, not a mix");if(typeof t!="function"&&!s.includes(t))throw new Error(`oneOf() default ${JSON.stringify(t)} is not one of ${s.join("|")}`);return{type:o?Number:String,reflect:r,...e?{attribute:e}:{},arc:{kind:"enum",values:[...s],default:t,derived:n,numeric:o}}}function Ge({default:s=0,min:t,max:e,step:r,clamp:n=null,int:o=!1,nullable:i=!1,attribute:a,reflect:l=!1}={}){if(i&&s===0&&(s=null),n&&n!=="toRange")throw new Error(`unknown clamp mode ${n}`);if(n&&t===void 0&&e===void 0)throw new Error('clamp: "toRange" needs a min and/or a max to clamp to');return{type:Number,reflect:l,...a?{attribute:a}:{},arc:{kind:"number",default:s,min:t,max:e,step:r,clamp:n,int:o,nullable:i}}}var fe=(s={})=>Ge({...s,int:!0});function Dn(s){return s.map(Number).filter(Number.isFinite)}function In(s){return s.every(t=>typeof t=="number"&&Number.isFinite(t))}function bt(s,t){return typeof t.default=="function"?t.default(s):t.default}function er(s,t){if(t===void 0)return;if(typeof t=="number")return t;let e=typeof s[t]=="function"?s[t]():s[t];return typeof e=="number"?e:void 0}function Un(s,t,e){if(t.blockedBy&&s[t.blockedBy])return bt(s,t);if(t.nullable&&(e==null||e===""))return null;if(t.kind==="flag")return typeof e=="boolean"?e:bt(s,t);if(t.kind==="enum"){let r=t.numeric&&typeof e=="string"?Number(e):e;return t.values.includes(r)?r:bt(s,t)}if(t.kind==="list")return Array.isArray(e)?t.numeric&&!In(e)?Dn(e):e:bt(s,t);if(t.kind==="number"){let r=typeof e=="number"?e:Number(e);if(!Number.isFinite(r))return bt(s,t);if(t.int&&(r=Math.trunc(r)),t.clamp==="toRange"){let n=er(s,t.min),o=er(s,t.max);n!==void 0&&(r=Math.max(n,r)),o!==void 0&&(r=Math.min(o,r))}return r}return e}function Tt(s){let t=[];for(let[e,r]of s.elementProperties??[])r?.["arc"]&&t.push([e,r.arc]);return t}function qn(s,t){for(let e=s;e;e=Object.getPrototypeOf(e)){let r=Object.getOwnPropertyDescriptor(e,t);if(r)return r}return null}var pe=Symbol("arc.blocked");function Hn(s){if(!Object.prototype.hasOwnProperty.call(s,pe)){Object.defineProperty(s,pe,{value:!0});for(let[t,e]of Tt(s)){if(!e.blockedBy)continue;let r=qn(s.prototype,t);if(!r?.set||!r?.get||r.get[pe])continue;let n=function(){return r.get.call(this)};n[pe]=!0,Object.defineProperty(s.prototype,t,{configurable:!0,enumerable:r.enumerable,get:n,set(o){this[e.blockedBy]&&o!==e.default||r.set.call(this,o)}})}}}var D=s=>class extends s{constructor(...t){super(...t),Hn(this.constructor);for(let[e,r]of Tt(this.constructor))this[e]===void 0&&(this[e]=bt(this,r));this.addController({hostUpdate:()=>{for(let[e,r]of Tt(this.constructor)){let n=this[e],o=Un(this,r,n);o!==n&&!Number.isNaN(o)&&(this[e]=o)}},hostUpdated:()=>{for(let[e,r]of Tt(this.constructor))r.kind!=="flag"||!r.negative||(this[e]===r.default?this.removeAttribute(r.negative):this.setAttribute(r.negative,""))}})}connectedCallback(){!this.hasUpdated&&this.shadowRoot!==null&&(this[We]=!0),super.connectedCallback();for(let[t,e]of Tt(this.constructor))e.kind==="flag"&&e.negative&&this.hasAttribute(e.negative)&&(this[t]=!e.default)}shouldUpdate(t){if(this[We]){this[We]=!1;let e={};for(let[r,n]of Tt(this.constructor)){if(n.kind!=="list")continue;let o=Nn(this,r,n);JSON.stringify(this[r])!==JSON.stringify(o)&&(e[r]=this[r],this[r]=o)}Object.keys(e).length&&this.updateComplete.then(()=>queueMicrotask(()=>Object.assign(this,e)))}return super.shouldUpdate(t)}};var rt=class extends D(C){constructor(){super(),this.href="",this._hasPrefix=!1,this._hasSuffix=!1,this._slottedAnchor=!1}_handleClick(){if(this.type!=="submit"&&this.type!=="reset")return;let t=this.closest("arc-form, form");t&&(t.tagName==="FORM"?this.type==="submit"?t.requestSubmit():t.reset():this.type==="submit"?t.submit():t.reset())}_onPrefixSlotChange(t){this._hasPrefix=t.target.assignedNodes({flatten:!0}).length>0}_onSuffixSlotChange(t){this._hasSuffix=t.target.assignedNodes({flatten:!0}).length>0}_onDefaultSlotChange(t){this._slottedAnchor=Qs(t.target)}_renderContent(){return w`
      ${this.loading?w`<span class="btn__spinner" aria-hidden="true"></span>`:""}
      <span class="btn__prefix ${this._hasPrefix?"":"btn__prefix--empty"}">
        <slot name="prefix" @slotchange=${this._onPrefixSlotChange}></slot>
      </span>
      <span class="btn__label"><slot @slotchange=${this._onDefaultSlotChange}></slot></span>
      <span class="btn__suffix ${this._hasSuffix?"":"btn__suffix--empty"}">
        <slot name="suffix" @slotchange=${this._onSuffixSlotChange}></slot>
      </span>
    `}firstUpdated(){st(this)}render(){if(this.href){let t=this.disabled||this.loading;return w`<a class="btn" href=${t?$:this.href} role=${t?"link":$} aria-disabled=${t?"true":$} part="base button">${this._renderContent()}</a>`}return this._slottedAnchor?w`<slot class="btn-slot" @slotchange=${this._onDefaultSlotChange}></slot>`:w`<button class="btn" type=${this.type} ?disabled=${this.disabled||this.loading} aria-busy=${this.loading?"true":"false"} @click=${this._handleClick} part="base button">${this._renderContent()}</button>`}};x(rt,"properties",{variant:q(["primary","secondary","ghost"]),size:q(["sm","md","lg"],{default:"md"}),href:{type:String},disabled:j(!1),loading:j(!1),type:q(["button","submit","reset"],{reflect:!1}),_hasPrefix:{state:!0},_hasSuffix:{state:!0},_slottedAnchor:{state:!0}}),x(rt,"styles",[L,Js,A`
      :host { display: inline-flex; }
      :host([disabled]),
      :host([loading]) { pointer-events: none; }

      :host([loading]) .btn { opacity: 0.7; }

      /* Anchor-adoption form: the slotted <a> *is* the control, so it takes the
         same box styling as .btn. The slot itself is display:contents (UA
         default), so the anchor becomes the host's flex item directly. Rules
         below pair .btn with .btn-slot::slotted(a) rather than duplicating
         declarations; keep the two in step when editing either. */

      .btn__spinner {
        display: none;
        width: 14px;
        height: 14px;
        border: 2px solid currentColor;
        border-top-color: transparent;
        border-radius: var(--radius-full);
        animation: arc-btn-spin 600ms linear infinite;
      }

      :host([loading]) .btn__spinner { display: inline-block; }
      :host([loading]) .btn__label { opacity: 0.6; }

      @keyframes arc-btn-spin {
        to { transform: rotate(360deg); }
      }

      .btn,
      .btn-slot::slotted(a) {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-sm);
        font-family: var(--font-label);
        font-weight: var(--font-label-weight, 600);
        text-transform: uppercase;
        letter-spacing: var(--label-spacing);
        border: 1px solid transparent;
        /* Pill. Circles are the house shape (the library is called ARC) and
           the round icon-only controls, the tags, the badges and the toggles
           already read that way; a rounded rectangle here was the odd one out
           on a row that contains all of them. Breaking, and deliberately so:
           there is no opt-out prop, because one shape being the shape is the
           point. Groups follow via --_group-radius in button-group.js. */
        border-radius: var(--radius-full);
        cursor: pointer;
        transition:
          background var(--transition-base),
          border-color var(--transition-base),
          box-shadow var(--transition-base),
          color var(--transition-base),
          transform 120ms var(--ease-out-expo);
        text-decoration: none;
        white-space: nowrap;
        box-sizing: border-box;
        min-height: var(--touch-min);
      }

      /* Sizes */
      :host([size="sm"]) .btn,
      :host([size="sm"]) .btn-slot::slotted(a) { font-size: var(--_text-xs); padding: var(--space-xs) var(--space-md); }
      :host(:not([size="lg"]):not([size="sm"])) .btn,
      :host(:not([size="lg"]):not([size="sm"])) .btn-slot::slotted(a),
      :host([size="md"]) .btn,
      :host([size="md"]) .btn-slot::slotted(a) { font-size: var(--_text-xs); padding: var(--space-sm) var(--space-lg); }
      :host([size="lg"]) .btn,
      :host([size="lg"]) .btn-slot::slotted(a) { font-size: var(--_text-xs); padding: var(--space-md) var(--space-xl); letter-spacing: var(--label-spacing); }

      /* Default → primary */
      :host(:not([variant="ghost"]):not([variant="secondary"])) .btn,
      :host(:not([variant="ghost"]):not([variant="secondary"])) .btn-slot::slotted(a) {
        background: var(--interactive);
        color: var(--on-accent);
        border-color: var(--interactive);
      }
      :host(:not([variant="ghost"]):not([variant="secondary"])) .btn:hover,
      :host(:not([variant="ghost"]):not([variant="secondary"])) .btn-slot::slotted(a:hover) { box-shadow: var(--interactive-active); }

      /* :active scale */
      :host(:not([variant="ghost"]):not([variant="secondary"])) .btn:active,
      :host(:not([variant="ghost"]):not([variant="secondary"])) .btn-slot::slotted(a:active),
      :host([variant="primary"]) .btn:active,
      :host([variant="primary"]) .btn-slot::slotted(a:active) { transform: scale(0.97); box-shadow: 0 0 8px rgba(var(--interactive-rgb),0.5); }
      :host([variant="secondary"]) .btn:active,
      :host([variant="secondary"]) .btn-slot::slotted(a:active) {
        transform: scale(0.97);
        background: rgba(var(--interactive-rgb),0.05);
      }
      :host([variant="ghost"]) .btn:active,
      :host([variant="ghost"]) .btn-slot::slotted(a:active) {
        transform: scale(0.97);
        background: var(--surface-overlay);
      }

      /* Prefix / Suffix */
      .btn__prefix,
      .btn__suffix {
        display: inline-flex;
        align-items: center;
      }

      .btn__prefix--empty,
      .btn__suffix--empty { display: none; }

      ::slotted([slot="prefix"]),
      ::slotted([slot="suffix"]) {
        display: flex;
      }
    `]),x(rt,"slotReaders",{prefix:"_onPrefixSlotChange","":"_onDefaultSlotChange",suffix:"_onSuffixSlotChange"});customElements.get("arc-button")||customElements.define("arc-button",rt);rt[Symbol.for("tagName")]="arc-button";var sr=A`
  /* Default, for a consumer that sets no variant at all. arc-alert and its
     siblings default to info in the constructor and never see this; arc-badge
     and arc-tag have no default variant, and without it their status glow
     would resolve against an undefined --_status-rgb and not paint. */
  :host {
    --_status-color: var(--accent-primary);
    --_status-rgb:   var(--accent-primary-rgb);
  }

  /* info is the accent, not --color-info. The two were both in use: statusVars
     said accent-primary, arc-badge and arc-tag said --color-info, which made
     "info" mean two different blues depending on which component you asked.
     Settled here, since this is the shared mechanism. */
  :host([variant="info"]),
  :host([variant="primary"]) {
    --_status-color: var(--accent-primary);
    --_status-rgb:   var(--accent-primary-rgb);
  }

  :host([variant="secondary"]) {
    --_status-color: var(--accent-secondary);
    --_status-rgb:   var(--accent-secondary-rgb);
  }

  :host([variant="success"]),
  :host([variant="tip"]) {
    --_status-color: var(--color-success);
    --_status-rgb:   var(--color-success-rgb);
  }

  :host([variant="warning"]) {
    --_status-color: var(--color-warning);
    --_status-rgb:   var(--color-warning-rgb);
  }

  :host([variant="error"]) {
    --_status-color: var(--color-error);
    --_status-rgb:   var(--color-error-rgb);
  }
`;var vt=class extends D(C){constructor(){super(),this.color=""}render(){let t=this.color?`border-color: rgba(${this.color}, 0.2); color: color-mix(in srgb, rgb(${this.color}), var(--text-primary) var(--accent-text-mix, 0%)); background: rgba(${this.color}, 0.06);`:"";return w`<span class="badge" part="base badge" style=${t}
      @mouseenter=${this.color?e=>{e.currentTarget.style.boxShadow=`0 0 12px rgba(${this.color}, 0.15)`}:null}
      @mouseleave=${this.color?e=>{e.currentTarget.style.boxShadow=""}:null}
    ><slot></slot></span>`}};x(vt,"properties",{variant:q(["default","primary","secondary","success","warning","error","info"]),size:q(["sm","md","lg"],{default:"md"}),color:{type:String}}),x(vt,"styles",[L,sr,A`
      :host { display: inline-flex; }

      .badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-xs);
        font-family: var(--font-mono);
        font-weight: var(--font-body-weight, 500);
        font-size: var(--_text-xs);
        letter-spacing: normal;
        text-transform: none;
        color: var(--text-muted);
        padding: var(--space-xs) var(--space-sm);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-full);
        background: var(--surface-hover);
        transition: box-shadow var(--transition-base), border-color var(--transition-base);
        line-height: var(--ui-lh);
      }

      :host([variant="primary"]) .badge {
        border-color: var(--accent-primary-border);
        color: color-mix(in srgb, var(--accent-primary), var(--text-primary) var(--accent-text-mix, 0%));
        background: rgba(var(--accent-primary-rgb), 0.06);
      }

      :host([variant="secondary"]) .badge {
        border-color: var(--accent-secondary-border);
        color: color-mix(in srgb, var(--accent-secondary), var(--text-primary) var(--accent-text-mix, 0%));
        background: rgba(var(--accent-secondary-rgb), 0.06);
      }

      :host([variant="success"]) .badge {
        border-color: rgba(var(--color-success-rgb), 0.2);
        color: color-mix(in srgb, var(--color-success), var(--text-primary) var(--accent-text-mix, 0%));
        background: rgba(var(--color-success-rgb), 0.06);
      }

      :host([variant="warning"]) .badge {
        border-color: rgba(var(--color-warning-rgb), 0.2);
        color: color-mix(in srgb, var(--color-warning), var(--text-primary) var(--accent-text-mix, 0%));
        background: rgba(var(--color-warning-rgb), 0.06);
      }

      :host([variant="error"]) .badge {
        border-color: rgba(var(--color-error-rgb), 0.2);
        color: color-mix(in srgb, var(--color-error), var(--text-primary) var(--accent-text-mix, 0%));
        background: rgba(var(--color-error-rgb), 0.06);
      }

      :host([variant="info"]) .badge {
        border-color: rgba(var(--color-info-rgb), 0.2);
        color: var(--color-info);
        background: rgba(var(--color-info-rgb), 0.06);
      }

      /* One hover rule for every variant: --glow-status takes its color from
         the --_status-rgb that statusVars sets on the host. This was six rules
         saying the same thing in six colors. The border is left
         alone, hover adds light, it does not move the edge. */
      :host(:hover) .badge { box-shadow: var(--glow-status); }

      /* Sizes */
      :host([size="sm"]) .badge { font-size: calc(var(--_text-xs) - 1px); padding: 2px var(--space-xs); }
      :host([size="lg"]) .badge { font-size: var(--_text-sm); padding: var(--space-sm) var(--space-md); }
    `]);customElements.get("arc-badge")||customElements.define("arc-badge",vt);vt[Symbol.for("tagName")]="arc-badge";var Ke=class{constructor(t,e,r,n){this.host=t,this._resolve=e,this._attach=r,this._detach=n,this._target=null,t.addController(this)}hostConnected(){this._sync()}hostUpdated(){this._sync()}hostDisconnected(){this._release()}_sync(){let t=this._resolve();t!==this._target&&(this._release(),t&&(this._target=t,this._attach(t)))}_release(){this._target&&(this._detach(this._target),this._target=null)}};function jn(s,t){return typeof t=="function"?()=>t(s):()=>s.shadowRoot?.querySelector(t)??null}function rr(s,t,e){if(typeof ResizeObserver>"u")return null;let r=jn(s,t),n=null;return new Ke(s,r,o=>{n??(n=new ResizeObserver(()=>e(o))),n.observe(o)},o=>n?.unobserve(o))}function nr(s,t,e,r){return e<s?e:e+r>s+t?e+r-t:s}var nt=class extends D(C){get _maxIndex(){return this._tabs?.length?this._tabs.length-1:void 0}constructor(){super(),this._tabs=[],rr(this,".tabs__list",()=>this._syncIndicator({instant:!0}))}_syncIndicator({instant:t=!1}={}){let e=this.shadowRoot,r=e?.querySelector(".tabs__ind");if(!r)return;let n=e.querySelectorAll(".tabs__tab")[this.selected];if(!n){r.classList.remove("is-on");return}t&&r.classList.add("is-instant"),r.style.setProperty("--_ind-x",`${n.offsetLeft}px`),r.style.setProperty("--_ind-y",`${n.offsetTop}px`),r.style.setProperty("--_ind-w",`${n.offsetWidth}px`),r.style.setProperty("--_ind-h",`${n.offsetHeight}px`),r.classList.add("is-on"),t&&(r.offsetWidth,r.classList.remove("is-instant")),this._revealInBar(n,t)}_revealInBar(t,e){let r=this.shadowRoot?.querySelector(".tabs__list");if(!r)return;let n=nr(r.scrollLeft,r.clientWidth,t.offsetLeft,t.offsetWidth),o=nr(r.scrollTop,r.clientHeight,t.offsetTop,t.offsetHeight);n===r.scrollLeft&&o===r.scrollTop||r.scrollTo({left:n,top:o,behavior:e?"instant":"auto"})}_playPanelEnter(){let t=this.shadowRoot?.querySelector(".tabs__panel");t&&(t.classList.remove("is-entering"),t.offsetWidth,t.classList.add("is-entering"))}_onSlotChange(t){let r=t.target.assignedElements({flatten:!0}).filter(n=>n.tagName==="ARC-TAB");this._tabs=r,this._syncVisibility()}_syncVisibility(){this._tabs.forEach((t,e)=>{t.hidden=e!==this.selected})}_isDisabled(t){return this._tabs[t]?.disabled===!0}_seek(t,e){let r=this._tabs.length;for(let n=1;n<=r;n+=1){let o=(t+e*n+r*n)%r;if(!this._isDisabled(o))return o}}_select(t){if(this._isDisabled(t))return;this.selected=t,this._syncVisibility();let e=this._tabs[t]?.label;this.dispatchEvent(new CustomEvent("arc-change",{detail:{value:t,label:e},bubbles:!0,composed:!0}))}_handleKeydown(t){let e=[...this.shadowRoot.querySelectorAll(".tabs__tab")],r=e.indexOf(t.target),n,o=this.orientation==="vertical",i=o?"ArrowDown":"ArrowRight",a=o?"ArrowUp":"ArrowLeft";if(t.key===i)n=this._seek(r,1);else if(t.key===a)n=this._seek(r,-1);else if(t.key==="Home")n=this._seek(-1,1);else if(t.key==="End")n=this._seek(e.length,-1);else return;t.preventDefault(),n!==void 0&&(e[n].focus(),this._select(n))}updated(t){let e=t.has("selected");e&&this._syncVisibility(),this._syncIndicator({instant:!e}),e&&t.get("selected")!==void 0&&this._playPanelEnter()}firstUpdated(){st(this),this._syncIndicator({instant:!0})}render(){return w`
      <div class="tabs" part="base tabs">
        <div class="tabs__list" role="tablist" aria-orientation=${this.orientation} @keydown=${this._handleKeydown}>
          <!--
            Hidden from assistive tech rather than given a role: a tablist's
            children are tabs, and this one is light. What it marks is already
            said by aria-selected on the button underneath it.
          -->
          <div class="tabs__ind" part="indicator" aria-hidden="true"></div>
          ${this._tabs.map((t,e)=>w`
            <button
              class="tabs__tab"
              role="tab"
              aria-selected=${e===this.selected?"true":"false"}
              ?disabled=${t.disabled===!0}
              tabindex=${e===this.selected?"0":"-1"}
              id="tab-${e}"
              aria-controls="panel"
              @click=${()=>this._select(e)}
            >${t.label}</button>
          `)}
        </div>

        <!--
          One panel, one id. Every tab's aria-controls points at it because
          every tab controls it. The panel does not swap elements, it swaps
          which arc-tab child is unhidden inside it. Per-tab ids were the
          defect: only the selected tab's reference resolved (finding #2).
        -->
        <div
          class="tabs__panel"
          role="tabpanel"
          id="panel"
          aria-labelledby="tab-${this.selected}"
        >
          <slot @slotchange=${this._onSlotChange}></slot>
        </div>
      </div>
    `}};x(nt,"properties",{selected:fe({default:0,min:0,max:"_maxIndex",clamp:"toRange",reflect:!0}),align:q(["start","center","end"]),variant:q(["underline","pills"]),orientation:q(["horizontal","vertical"]),_tabs:{state:!0}}),x(nt,"styles",[L,A`
      :host {
        display: block;
        /* The indicator's light. A lobe shape substitutes its var()s at the
           element that declares it, and the shapes are declared on :host: an
           input set on the indicator itself would paint in the fallback color
           with nothing failing. */
        --lobe-rgb: var(--interactive-rgb);
        --lobe-alpha: 1;
      }

      .tabs__list {
        position: relative;
        display: flex;
        border-bottom: 1px solid var(--divider);
        gap: var(--space-xs);
        overflow-x: auto;
        overflow-y: hidden;
        scroll-behavior: smooth;
        /* A scrollbar here would lie directly on the divider and read as a
           second rule under the bar. Overflow announces itself through the
           half-cut tab at the edge, and the selection scrolls itself into
           view, so nothing depends on the bar being visible. */
        scrollbar-width: none;
      }

      .tabs__list::-webkit-scrollbar { display: none; }

      /* Alignment */
      :host([align="center"]) .tabs__list { justify-content: center; }
      :host([align="end"]) .tabs__list { justify-content: flex-end; }

      /* ── The indicator ──
         One element for every variant and orientation: the component hands it
         the selected button's box and CSS decides what to paint inside that
         box. This is what makes a selection *travel*: the tab you left and
         the tab you chose are connected by the same piece of light moving
         between them, which is the one authored moment here. Everything else
         in the bar stays quiet so the move stays legible. */
      .tabs__ind {
        position: absolute;
        top: 0;
        left: 0;
        z-index: 0;
        width: var(--_ind-w, 0px);
        height: var(--_ind-h, 0px);
        transform: translate(var(--_ind-x, 0px), var(--_ind-y, 0px));
        pointer-events: none;
        opacity: 0;
        transition:
          transform var(--duration-base) var(--ease-out),
          width var(--duration-base) var(--ease-out),
          height var(--duration-base) var(--ease-out),
          opacity var(--transition-fast);
      }

      /* Measured for the first time, or re-measured after a resize. Neither is
         a selection, so neither travels. Without this the indicator flies in
         from the list's origin on load and lurches on every reflow. */
      .tabs__ind.is-instant { transition: none; }

      .tabs__ind.is-on { opacity: 1; }

      /* Underline: a lobe laid along the divider, brightest under the label
         and thinning to nothing at both ends, rather than a 2px rectangle
         that starts and stops. */
      .tabs__ind::after {
        content: '';
        position: absolute;
        inset-inline: 0;
        bottom: 0;
        height: 2px;
        background: var(--lobe-line);
        box-shadow: 0 0 10px rgba(var(--interactive-rgb), 0.45);
      }

      /* …and the light that line throws back up into the tab it marks. Glow
         over definition: the selected tab is lit, not outlined. */
      .tabs__ind::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(
          to top,
          rgba(var(--interactive-rgb), 0.14),
          rgba(var(--interactive-rgb), 0) 72%
        );
      }

      .tabs__tab {
        position: relative;
        z-index: 1;
        font-family: var(--font-label);
        font-weight: var(--font-label-weight, 600);
        font-size: var(--_text-xs);
        letter-spacing: var(--label-spacing);
        text-transform: uppercase;
        color: var(--text-ghost);
        background: none;
        border: none;
        padding: var(--touch-pad) var(--space-md);
        min-height: var(--touch-min);
        cursor: pointer;
        /* Not a state: the gutter the indicator's line sits in, and the 1px
           of overlap that puts it on top of the divider rather than above it. */
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0;
        transition:
          color var(--transition-fast),
          background var(--transition-fast),
          transform 150ms var(--ease-out);
        white-space: nowrap;
      }

      .tabs__tab:hover:not(:disabled):not([aria-selected="true"]) {
        color: var(--text-primary);
        background: rgba(var(--text-primary-rgb), 0.045);
      }

      .tabs__tab:active:not(:disabled) { transform: scale(0.97); }

      .tabs__tab:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      /* The selected tab lifts to the accent and stops there. Its ground, its
         underline and its glow all belong to the indicator, so that they can
         move. */
      .tabs__tab[aria-selected="true"] { color: var(--interactive); }

      /* Pills variant */
      :host([variant="pills"]) .tabs__list {
        border-bottom: none;
        gap: var(--space-xs);
      }

      :host([variant="pills"]) .tabs__tab {
        border-bottom: none;
        margin-bottom: 0;
        border-radius: var(--radius-sm);
      }

      :host([variant="pills"]) .tabs__tab:hover:not(:disabled):not([aria-selected="true"]) {
        background: rgba(var(--text-primary-rgb), 0.08);
      }

      /* The travelling line is an underline's device; a pill's is the ground
         itself, which the same element becomes. */
      :host([variant="pills"]) .tabs__ind::after { display: none; }

      :host([variant="pills"]) .tabs__ind::before {
        background: rgba(var(--interactive-rgb), 0.12);
        border-radius: var(--radius-sm);
        box-shadow: var(--interactive-hover);
      }

      .tabs__tab:focus-visible {
        outline: none;
        box-shadow: var(--interactive-focus-ring);
        border-radius: var(--radius-sm);
      }

      .tabs__panel {
        padding: var(--space-lg) 0;
        color: var(--text-secondary);
        font-size: var(--body-size);
        line-height: var(--body-lh);
      }

      /* The panel does not cut; it arrives, once, on the switch that caused
         it. The docs have promised this transition since v2. */
      .tabs__panel.is-entering {
        animation: tabs-panel-in var(--duration-enter) var(--ease-out) both;
      }

      @keyframes tabs-panel-in {
        from {
          opacity: 0;
          transform: translateY(4px);
        }
      }

      .tabs__panel[hidden] { display: none; }

      /* ── Vertical orientation ── */
      :host([orientation="vertical"]) .tabs {
        display: flex;
        flex-direction: row;
      }

      :host([orientation="vertical"]) .tabs__list {
        flex-direction: column;
        border-bottom: none;
        border-inline-end: 1px solid var(--divider);
        overflow-y: auto;
        overflow-x: hidden;
        min-width: 180px;
      }

      :host([orientation="vertical"]) .tabs__tab {
        border-bottom: none;
        margin-bottom: 0;
        margin-inline-end: var(--space-xs);
        border-radius: var(--radius-sm);
        text-align: start;
      }

      /* State is tint, glow and accent text. A colored edge down the side of
         the selected tab is the house's hardest ban, and the
         rail beside it is structure (one flat --divider that never changes
         colour), so the selection has to be carried by light instead. */
      :host([orientation="vertical"]) .tabs__ind::after { display: none; }

      :host([orientation="vertical"]) .tabs__ind::before {
        background: rgba(var(--interactive-rgb), 0.12);
        border-radius: var(--radius-sm);
        box-shadow: inset 0 0 14px -6px rgba(var(--interactive-rgb), 0.9);
      }

      :host([orientation="vertical"]) .tabs__panel {
        padding: 0 0 0 var(--space-lg);
        flex: 1;
        min-width: 0;
      }

      /* Vertical + Pills variant */
      :host([orientation="vertical"][variant="pills"]) .tabs__list {
        border-inline-end: none;
      }

      :host([orientation="vertical"][variant="pills"]) .tabs__tab {
        margin-inline-end: 0;
      }

      @media (prefers-reduced-motion: reduce) {
        .tabs__list { scroll-behavior: auto; }
        .tabs__ind,
        .tabs__tab { transition: none; }
        .tabs__panel.is-entering { animation: none; }
      }
    `]),x(nt,"slotReaders",{"":"_onSlotChange"});var yt=class extends D(C){constructor(){super(),this.label=""}updated(t){tr(this,t,["label","disabled"])}render(){return w`<slot></slot>`}};x(yt,"properties",{label:{type:String,reflect:!0},disabled:j(!1)}),x(yt,"styles",A`
    :host { display: block; }
    :host([hidden]) { display: none; }
  `);customElements.get("arc-tab")||customElements.define("arc-tab",yt);yt[Symbol.for("tagName")]="arc-tab";customElements.get("arc-tabs")||customElements.define("arc-tabs",nt);nt[Symbol.for("tagName")]="arc-tabs";var _t=class extends D(C){constructor(){super(),this.value=0,this.prefix="",this.suffix="",this.decimals=0,this.locale="en-US",this._displayValue=0,this._previousValue=0,this._rafId=null}disconnectedCallback(){super.disconnectedCallback(),this._rafId!=null&&(cancelAnimationFrame(this._rafId),this._rafId=null)}willUpdate(t){if(t.has("value")){let e=t.get("value");this._previousValue=e??0,this._animate(this._previousValue,this.value)}}_easeOutExpo(t){return t===1?1:1-Math.pow(2,-10*t)}_prefersReducedMotion(){return typeof window>"u"?!0:window.matchMedia?.("(prefers-reduced-motion: reduce)").matches}_animate(t,e){if(this._rafId!=null&&(cancelAnimationFrame(this._rafId),this._rafId=null),this._prefersReducedMotion()||this.duration<=0){this._displayValue=e,this.requestUpdate();return}let r=performance.now(),n=e-t,o=i=>{let a=i-r,l=Math.min(a/this.duration,1),c=this._easeOutExpo(l);this._displayValue=t+n*c,this.requestUpdate(),l<1?this._rafId=requestAnimationFrame(o):(this._displayValue=e,this._rafId=null,this.requestUpdate())};this._rafId=requestAnimationFrame(o)}_formatValue(t){let e={minimumFractionDigits:this.decimals,maximumFractionDigits:this.decimals};this.format==="currency"?this.prefix||(e.style="currency",e.currency="USD"):this.format;let r;try{r=new Intl.NumberFormat(this.locale,e).format(t)}catch{r=t.toFixed(this.decimals)}let n=[];return this.prefix&&n.push(this.prefix),n.push(r),this.format==="percent"&&!this.suffix?n.push("%"):this.suffix&&n.push(this.suffix),n.join("")}render(){return w`
      <span class="value"
            part="base value"
            role="status"
            aria-live="polite"
      >${this._formatValue(this._displayValue)}</span>
    `}};x(_t,"properties",{value:{type:Number,reflect:!0},duration:Ge({default:1e3,min:0,clamp:"toRange"}),format:q(["number","currency","percent"]),prefix:{type:String},suffix:{type:String},decimals:{type:Number},locale:{type:String}}),x(_t,"styles",[L,A`
      :host {
        display: inline-block;
        font-family: var(--font-mono);
        font-variant-numeric: tabular-nums;
      }

      .value {
        white-space: nowrap;
      }
    `]);customElements.get("arc-animated-number")||customElements.define("arc-animated-number",_t);_t[Symbol.for("tagName")]="arc-animated-number";var ot=class extends D(C){constructor(){super(),this._items=[]}_onSlotChange(t){this._items=t.target.assignedElements({flatten:!0}).filter(e=>e.tagName==="ARC-TIMELINE-ITEM")}firstUpdated(){st(this)}render(){return w`
      <div part="base" class="timeline__slot-host">
        <slot @slotchange=${this._onSlotChange}></slot>
      </div>
      <ol class="timeline" part="timeline" role="list">
        ${this._items.map(t=>w`
            <li class="timeline__item" part="item">
              <div class="timeline__marker" part="marker">
                <span class="timeline__dot" part="dot"></span>
                <span class="timeline__line" part="line"></span>
              </div>
              <div class="timeline__content" part="content">
                <div class="timeline__title" part="title" role="heading" aria-level=${this.headingLevel}>${t.heading||""}</div>
                ${t.description?w`<p class="timeline__desc" part="description">${t.description}</p>`:""}
                ${t.date?w`<time class="timeline__date" part="date">${t.date}</time>`:""}
              </div>
            </li>
          `)}
      </ol>
    `}};x(ot,"properties",{headingLevel:fe({default:3,min:1,clamp:"toRange",attribute:"heading-level"}),_items:{state:!0}}),x(ot,"styles",[L,A`
      :host { display: block; }

      .timeline {
        display: flex;
        flex-direction: column;
        gap: 0;
        padding: 0;
        margin: 0;
        list-style: none;
      }

      .timeline__item {
        display: flex;
        gap: var(--space-lg);
        position: relative;
        padding-bottom: var(--space-xl);
      }

      .timeline__item:last-child { padding-bottom: 0; }

      .timeline__marker {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex-shrink: 0;
        width: 24px;
        position: relative;
      }

      .timeline__dot {
        width: 12px;
        height: 12px;
        border-radius: var(--radius-full);
        background: var(--accent-primary);
        border: 2px solid var(--surface-base);
        box-shadow:
          0 0 0 1px rgba(var(--accent-primary-rgb), 0.3),
          var(--glow-sm);
        flex-shrink: 0;
        z-index: 1;
        position: relative;
        transition: box-shadow var(--transition-fast), transform var(--transition-fast);
      }

      .timeline__item:hover .timeline__dot {
        box-shadow:
          0 0 0 2px rgba(var(--accent-primary-rgb), 0.4),
          0 0 14px rgba(var(--accent-primary-rgb), 0.4);
        transform: scale(1.2);
      }

      .timeline__line {
        position: absolute;
        top: 12px;
        bottom: calc(-1 * var(--space-xl));
        left: 50%;
        width: 1px;
        transform: translateX(-50%);
        background: linear-gradient(180deg, rgba(var(--accent-primary-rgb), 0.4), var(--border-default) 40%);
      }

      .timeline__item:last-child .timeline__line { display: none; }

      .timeline__content {
        flex: 1;
        min-width: 0;
        padding-top: 0;
      }

      .timeline__title {
        margin: 0;
        font-family: var(--font-label);
        font-size: var(--_text-xs);
        font-weight: var(--font-label-weight, 600);
        letter-spacing: var(--label-spacing);
        text-transform: uppercase;
        color: var(--text-primary);
        line-height: var(--ui-lh);
        transition: color var(--transition-fast);
      }

      .timeline__item:hover .timeline__title {
        color: var(--accent-primary);
      }

      .timeline__desc {
        margin: var(--space-sm) 0 0;
        font-family: var(--font-body);
        font-size: var(--_text-sm);
        line-height: var(--body-lh);
        color: var(--text-muted);
      }

      .timeline__date {
        margin: var(--space-sm) 0 0;
        font-family: var(--font-label);
        font-size: var(--_text-xs);
        font-weight: var(--font-label-weight, 600);
        letter-spacing: var(--label-spacing);
        text-transform: uppercase;
        color: var(--text-ghost);
      }

      .timeline__slot-host { display: none; }
    `]),x(ot,"slotReaders",{"":"_onSlotChange"});var xt=class extends C{constructor(){super(),this.heading="",this.date=""}get description(){return this.textContent.trim()}render(){return w`<slot></slot>`}};x(xt,"properties",{heading:{type:String,reflect:!0},date:{type:String,reflect:!0}}),x(xt,"styles",A`
    :host { display: none; }
  `);customElements.get("arc-timeline-item")||customElements.define("arc-timeline-item",xt);xt[Symbol.for("tagName")]="arc-timeline-item";customElements.get("arc-timeline")||customElements.define("arc-timeline",ot);ot[Symbol.for("tagName")]="arc-timeline";var or=s=>s??$;var wt=class extends D(C){constructor(){super(),this.src="",this.poster="",this.label="",this.controls=!0,this._started=!1,this._playing=!1,this._currentTime=0,this._duration=0,this._fullscreen=!1,this._controlsVisible=!0,this._scrubbing=!1,this._idleTimer=null}disconnectedCallback(){super.disconnectedCallback(),clearTimeout(this._idleTimer)}get _video(){return this.renderRoot?.querySelector("video")??null}_formatTime(t){let e=Number.isFinite(t)?Math.max(0,Math.floor(t)):0,r=Math.floor(e/3600),n=Math.floor(e%3600/60),o=e%60,i=a=>String(a).padStart(2,"0");return r>0?`${r}:${i(n)}:${i(o)}`:`${n}:${i(o)}`}_onPlay(t){this._started=!0,this._playing=!0,this.dispatchEvent(new CustomEvent("arc-play",{detail:{value:t.target.currentTime??0},bubbles:!0,composed:!0})),this._restartIdleTimer()}_onPause(t){this._playing=!1,clearTimeout(this._idleTimer),this._controlsVisible=!0,this.dispatchEvent(new CustomEvent("arc-pause",{detail:{value:t.target.currentTime??0},bubbles:!0,composed:!0}))}_onEnded(t){this.dispatchEvent(new CustomEvent("arc-ended",{detail:{value:t.target.currentTime??0},bubbles:!0,composed:!0}))}_onTimeUpdate(t){this._currentTime=t.target.currentTime??0}_onLoadedMetadata(t){let e=t.target.duration;this._duration=Number.isFinite(e)?e:0}_onActivity(){this._controlsVisible||(this._controlsVisible=!0),this._restartIdleTimer()}_restartIdleTimer(){clearTimeout(this._idleTimer),this._playing&&(this._idleTimer=setTimeout(()=>{this._playing&&!this._scrubbing&&(this._controlsVisible=!1)},2e3))}_togglePlay(){let t=this._video;t&&(t.paused?t.play()?.catch?.(()=>{}):t.pause())}_toggleMute(){this.muted=!this.muted;let t=this._video;t&&(t.muted=this.muted)}_toggleFullscreen(){let t=this.renderRoot?.querySelector(".video");!t||typeof t.requestFullscreen!="function"||(document.fullscreenElement?document.exitFullscreen?.():t.requestFullscreen()?.catch?.(()=>{}))}_onFullscreenChange(){this._fullscreen=!!document.fullscreenElement}_seekBy(t){let e=this._video;if(!e)return;let r=Number.isFinite(e.duration)?e.duration:0,n=Math.min(r,Math.max(0,(e.currentTime??0)+t));e.currentTime=n,this._currentTime=n}_onScrubInput(t){let e=Number(t.target.value),r=this._video;r&&(r.currentTime=e),this._currentTime=e}_onScrubDown(){this._scrubbing=!0,this._onActivity()}_onScrubUp(){this._scrubbing=!1,this._restartIdleTimer()}_onKeyDown(t){let e=t.composedPath()[0],r=e?.matches?.('input[type="range"]'),n=!!e?.closest?.("button");switch(t.key){case" ":if(n||r)return;t.preventDefault(),this._togglePlay();break;case"k":case"K":t.preventDefault(),this._togglePlay();break;case"ArrowRight":if(r)return;t.preventDefault(),this._seekBy(5);break;case"ArrowLeft":if(r)return;t.preventDefault(),this._seekBy(-5);break;case"m":case"M":t.preventDefault(),this._toggleMute();break;case"f":case"F":t.preventDefault(),this._toggleFullscreen();break;default:return}this._onActivity()}_muteGlyph(){return this.muted?w`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="22" y1="9" x2="16" y2="15"></line><line x1="16" y1="9" x2="22" y2="15"></line></svg>`:w`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>`}_fullscreenGlyph(){return this._fullscreen?w`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3v3a2 2 0 0 1-2 2H3"></path><path d="M21 8h-3a2 2 0 0 1-2-2V3"></path><path d="M3 16h3a2 2 0 0 1 2 2v3"></path><path d="M16 21v-3a2 2 0 0 1 2-2h3"></path></svg>`:w`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3H5a2 2 0 0 0-2 2v3"></path><path d="M21 8V5a2 2 0 0 0-2-2h-3"></path><path d="M3 16v3a2 2 0 0 0 2 2h3"></path><path d="M16 21h3a2 2 0 0 0 2-2v-3"></path></svg>`}_renderControls(){let t=this._duration,e=t>0?this._currentTime/t*100:0,r=!this._controlsVisible;return w`
      <div class="video__controls ${r?"video__controls--idle":""}" part="controls">
        <button
          class="video__button"
          part="play-toggle"
          aria-label=${this._playing?"Pause":"Play"}
          @click=${this._togglePlay}
        >
          <arc-icon name=${this._playing?"pause":"play"} size="sm"></arc-icon>
        </button>
        <span class="video__time" part="time">
          <span class="video__time-current">${this._formatTime(this._currentTime)}</span>
          <span aria-hidden="true">/</span>
          <span class="video__time-total">${this._formatTime(t)}</span>
        </span>
        <input
          class="video__scrubber"
          part="scrubber"
          type="range"
          min="0"
          max=${t>0?t:1}
          step="any"
          .value=${String(this._currentTime)}
          aria-label="Seek"
          aria-valuetext="${this._formatTime(this._currentTime)} of ${this._formatTime(t)}"
          style="--fill-percent: ${e}%"
          @input=${this._onScrubInput}
          @pointerdown=${this._onScrubDown}
          @pointerup=${this._onScrubUp}
          @pointercancel=${this._onScrubUp}
        />
        <button
          class="video__button"
          part="mute-button"
          aria-label=${this.muted?"Unmute":"Mute"}
          aria-pressed=${this.muted?"true":"false"}
          @click=${this._toggleMute}
        >${this._muteGlyph()}</button>
        <button
          class="video__button"
          part="fullscreen-button"
          aria-label=${this._fullscreen?"Exit fullscreen":"Fullscreen"}
          @click=${this._toggleFullscreen}
        >${this._fullscreenGlyph()}</button>
      </div>
    `}render(){let t=this.controls!==!1;return w`
      <div
        class="video"
        part="base wrapper"
        role="region"
        aria-label=${this.label||"Video player"}
        tabindex=${or(t?"0":void 0)}
        @keydown=${t?this._onKeyDown:$}
        @pointermove=${t?this._onActivity:$}
        @pointerdown=${t?this._onActivity:$}
        @focusin=${t?this._onActivity:$}
        @fullscreenchange=${this._onFullscreenChange}
      >
        <video
          part="video"
          src=${this.src||$}
          poster=${this.poster||$}
          preload=${this.preload}
          ?autoplay=${this.autoplay}
          ?loop=${this.loop}
          ?muted=${this.muted}
          .muted=${this.muted}
          playsinline
          @play=${this._onPlay}
          @pause=${this._onPause}
          @ended=${this._onEnded}
          @timeupdate=${this._onTimeUpdate}
          @loadedmetadata=${this._onLoadedMetadata}
          @durationchange=${this._onLoadedMetadata}
          @click=${this._started?this._togglePlay:$}
        ></video>
        ${this._started?$:w`
          <div class="video__overlay" part="overlay">
            <button
              class="video__play"
              part="play-button"
              aria-label=${this.label?`Play ${this.label}`:"Play video"}
              @click=${this._togglePlay}
            >
              <arc-icon name="play" size="xl"></arc-icon>
            </button>
          </div>
        `}
        ${t&&this._started?this._renderControls():$}
      </div>
    `}};x(wt,"properties",{src:{type:String},poster:{type:String},label:{type:String},autoplay:j(!1),loop:j(!1),muted:j(!1),controls:j(!0,{negative:"no-controls"}),preload:q(["none","metadata","auto"],{default:"metadata",reflect:!1}),_started:{state:!0},_playing:{state:!0},_currentTime:{state:!0},_duration:{state:!0},_fullscreen:{state:!0},_controlsVisible:{state:!0}}),x(wt,"styles",[L,A`
      :host {
        display: block;
      }

      .video {
        position: relative;
        overflow: hidden;
        aspect-ratio: 16/9;
        border-radius: var(--radius-md);
        background: var(--surface-base);
      }

      .video:focus-visible {
        outline: none;
        box-shadow: var(--interactive-focus-ring);
      }

      video {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
      }

      /* Pre-play overlay: the poster shows through, the play button carries
         the state - accent glyph, glow, and a brighter glow on approach. */
      .video__overlay {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .video__play {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 64px;
        height: 64px;
        padding: 0;
        border-radius: var(--radius-full);
        border: 1px solid var(--border-default);
        background: var(--surface-primary);
        color: var(--interactive);
        cursor: pointer;
        box-shadow: var(--glow-md);
        transition:
          box-shadow var(--transition-base),
          transform var(--transition-base);
      }

      .video__play:hover {
        box-shadow: var(--glow-primary);
        transform: scale(1.05);
      }

      .video__play:focus-visible {
        outline: none;
        box-shadow: var(--interactive-focus), var(--glow-md);
      }

      /* The glyph is a triangle pointing right; nudge it optically on-center. */
      .video__play arc-icon {
        margin-inline-start: 3px;
      }

      /* Control bar: a floating themed chip, not raw glyphs over an unknown
         frame - the same call arc-carousel makes for its arrows, and the only
         one that survives both themes over arbitrary video content. */
      .video__controls {
        position: absolute;
        inset-inline: var(--space-sm);
        inset-block-end: var(--space-sm);
        display: flex;
        align-items: center;
        gap: var(--space-sm);
        padding: var(--space-xs) var(--space-sm);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
        background: var(--surface-primary);
        transition:
          opacity var(--transition-base),
          transform var(--transition-base);
      }

      /* At rest the bar recedes rather than leaves: still legible, still
         clickable, just quiet enough to stop competing with the frame. It
         returns to full strength on approach, which is the affordance - you
         can always see where the controls are, so nothing has to be
         summoned by waving at the video. */
      .video__controls--idle {
        opacity: 0.45;
      }

      .video:hover .video__controls--idle,
      .video__controls--idle:hover,
      .video__controls--idle:focus-within {
        opacity: 1;
      }

      .video__button {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        flex: none;
        padding: 0;
        border: none;
        border-radius: var(--radius-sm);
        background: transparent;
        color: var(--text-primary);
        cursor: pointer;
        transition:
          color var(--transition-fast),
          background var(--transition-fast),
          box-shadow var(--transition-fast);
      }

      .video__button:hover {
        color: var(--interactive);
        background: var(--surface-hover);
        box-shadow: var(--glow-xs);
      }

      .video__button:focus-visible {
        outline: none;
        box-shadow: var(--interactive-focus-ring);
      }

      .video__button svg {
        width: 16px;
        height: 16px;
      }

      .video__time {
        display: flex;
        align-items: baseline;
        gap: var(--space-xs);
        font-family: var(--font-mono);
        font-size: var(--code-size);
        color: var(--text-muted);
        /* Updated every timeupdate - proportional digits would jitter. */
        font-variant-numeric: tabular-nums;
        user-select: none;
        white-space: nowrap;
      }

      .video__time-current {
        color: var(--interactive);
        font-weight: var(--font-label-weight, 600);
      }

      /* Scrubber: the slider track recipe, sized down for a control bar. */
      .video__scrubber {
        -webkit-appearance: none;
        appearance: none;
        flex: 1;
        min-width: 40px;
        height: 4px;
        margin: 0;
        padding: 0;
        border-radius: var(--radius-full);
        background: linear-gradient(
          to right,
          var(--interactive) 0%,
          var(--interactive) var(--fill-percent, 0%),
          var(--border-default) var(--fill-percent, 0%),
          var(--border-default) 100%
        );
        outline: none;
        cursor: pointer;
      }

      .video__scrubber::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 12px;
        height: 12px;
        border-radius: var(--radius-full);
        background: var(--interactive);
        border: 2px solid var(--surface-primary);
        cursor: pointer;
        box-shadow: var(--glow-xs);
        transition: box-shadow var(--transition-fast);
      }

      .video__scrubber::-moz-range-thumb {
        width: 12px;
        height: 12px;
        border-radius: var(--radius-full);
        background: var(--interactive);
        border: 2px solid var(--surface-primary);
        cursor: pointer;
        box-shadow: var(--glow-xs);
        transition: box-shadow var(--transition-fast);
      }

      /* The two thumb pseudo-elements cannot share a selector: a browser that
         does not recognize one drops the whole rule. */
      .video__scrubber:focus-visible::-webkit-slider-thumb {
        box-shadow: var(--interactive-focus-ring), var(--interactive-focus-thumb);
      }

      .video__scrubber:focus-visible::-moz-range-thumb {
        box-shadow: var(--interactive-focus-ring), var(--interactive-focus-thumb);
      }

      @media (prefers-reduced-motion: reduce) {
        .video__play,
        .video__button,
        .video__scrubber::-webkit-slider-thumb,
        .video__scrubber::-moz-range-thumb {
          transition: none;
        }

        .video__play:hover {
          transform: none;
        }

        /* Reduced motion drops the fade, not the dimming: the bar still
           recedes at rest, it just arrives there without the transition. */
        .video__controls {
          transition: none;
        }
      }
    `]);var ir={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},ar=s=>(...t)=>({_$litDirective$:s,values:t}),me=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,r){this._$Ct=t,this._$AM=e,this._$Ci=r}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};var Zt=class extends me{constructor(t){if(super(t),this.it=$,t.type!==ir.CHILD)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===$||t==null)return this._t=void 0,this.it=t;if(t===K)return t;if(typeof t!="string")throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this._t;this.it=t;let e=[t];return e.raw=e,this._t={_$litType$:this.constructor.resultType,strings:e,values:[]}}};Zt.directiveName="unsafeHTML",Zt.resultType=1;var lr=ar(Zt);function cr(s,t){if(!!1)return;let e=Object.entries(t).filter(([,o])=>o!=null&&o!=="");if(!e.length)return;let r=(s.getAttribute("style")??"").trim(),n=e.map(([o,i])=>`${o}: ${i}`).join("; ");s.setAttribute("style",r?`${r.replace(/;?$/,";")} ${n}`:n)}var Y='<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',Ye={x:`${Y}<path d="M6 6l12 12M18 6L6 18"/></svg>`,"chevron-left":`${Y}<path d="M15 6l-6 6 6 6"/></svg>`,"chevron-right":`${Y}<path d="M9 6l6 6-6 6"/></svg>`,"chevrons-left":`${Y}<path d="M11 6l-6 6 6 6M19 6l-6 6 6 6"/></svg>`,"chevrons-right":`${Y}<path d="M5 6l6 6-6 6M13 6l6 6-6 6"/></svg>`,"dots-three":`${Y}<path d="M5 12h.01M12 12h.01M19 12h.01"/></svg>`,pencil:`${Y}<path d="M4 20l1-4L16 5l3 3L8 19z"/><path d="M13.5 7.5l3 3"/></svg>`,play:`${Y}<path d="M7 5l12 7-12 7z"/></svg>`,pause:`${Y}<path d="M8 5v14M16 5v14"/></svg>`};var W={},F=null,Nt=new Map,hr=new Map,Fn="arc-icon-payload",dr=null;function ur(){if(typeof document>"u")return;let s=document.getElementById(Fn);if(!(!s||s===dr)){dr=s;try{let t=JSON.parse(s.textContent);for(let[e,r]of Object.entries(t))e in W||(W[e]=r)}catch{}}}var pr=new Set;function mr(s,t){let e=s??"";if(pr.has(e))return;pr.add(e);let r=[...Nt.keys()],n=Object.keys(W).length,o=t?`"${t}"`:"a named icon",i=s?`[arc-ui] Icon library "${s}" is not registered, so ${o} renders as an empty slot.`:n?`[arc-ui] ${o} is not in the custom icon map and no icon library is selected, so it renders as an empty slot. ${n} icon${n===1?"":"s"} registered by hand resolve normally; this is the first name that did not.`:`[arc-ui] No icon library is selected, so ${o} \u2014 and every other named icon \u2014 renders as an empty slot. (ARC's own close, chevron and edit glyphs are built in and still draw.)`,a=r.length?` Registered: ${r.join(", ")}. Select one with iconRegistry.use("${r[0]}").`:n?` Register it with iconRegistry.register(), or install a pack:
    npm i @arclux/arc-ui-icons
    import '@arclux/arc-ui-icons/phosphor';`:` Icon packs moved out of @arclux/arc-ui in v4:
    npm i @arclux/arc-ui-icons
    import '@arclux/arc-ui-icons/phosphor';
  See https://github.com/arclight-digital/arc-ui/blob/main/MIGRATION.md \u2014 "Icons moved to @arclux/arc-ui-icons".`;console.warn(i+a)}function Vn(s){let t=gr();return t||mr(F,s),t}function gr(){return F===null?null:Nt.get(F)??null}function fr(s,t=gr()){return!Object.hasOwn(Ye,s)||t&&(t.icons[t.aliases[s]??s]??t.icons[s])?null:Ye[s]}var Xt={register(s,t){if(typeof s!="string"||!s)throw new Error("iconRegistry.register: a library needs a name.");if(!t?.icons||typeof t.icons!="object")throw new Error(`iconRegistry.register("${s}"): expected { icons } mapping icon names to SVG sources or to functions that import them.`);Nt.set(s,{icons:t.icons,aliases:t.aliases??{}}),F===null&&(F=s)},libraries(){return[...Nt.keys()]},hasLibrary(){return F!==null&&Nt.has(F)},use(s){if(typeof s!="string"||!s)throw new Error("iconRegistry.use: expected a library name.");F=s},set(s){for(let[t,e]of Object.entries(s)){let r=t.replace(/([A-Z]+)([A-Z][a-z])/g,"$1-$2").replace(/([a-z])([A-Z])/g,"$1-$2").toLowerCase();W[r]=e}},async get(s){if(ur(),W[s])return W[s];let t=fr(s);if(t)return t;let e=Vn(s);if(!e)return null;try{let r=e.icons[e.aliases[s]??s]??e.icons[s];if(!r)return null;let n=typeof r=="function"?(await r()).default:r;return typeof n!="string"?null:(hr.set(`${F}:${s}`,n),n)}catch{return null}},getSync(s){return s?(ur(),W[s]?W[s]:hr.get(`${F}:${s}`)??fr(s)):null},async preload(s){await Promise.all([...new Set(s)].filter(Boolean).map(t=>this.get(t)))},async list(s){let t=s??F,e=t===null?null:Nt.get(t);return e?[...Object.keys(W),...Object.keys(e.icons)]:(mr(t),Object.keys(W))}};var Wn=/[\s\u0000-\u001F\u007F-\u009F]+/g;function br(s){return s.replace(Wn,"").toLowerCase()}function Gn(s,t){let e=s[t+1]==="/",r=t+(e?2:1),n=r;for(;r<s.length&&/[^\s/>]/.test(s[r]);)r++;let o=s.slice(n,r).toLowerCase(),i=[];for(;;){for(;r<s.length&&/\s/.test(s[r]);)r++;if(r>=s.length||s[r]===">"||s[r]==="/")break;let l=r;for(;r<s.length&&/[^\s=/>]/.test(s[r]);)r++;let c=s.slice(l,r);if(!c)break;let d=r;for(;d<s.length&&/\s/.test(s[d]);)d++;if(s[d]!=="="){i.push({name:c,value:null});continue}for(r=d+1;r<s.length&&/\s/.test(s[r]);)r++;let h=s[r],u;if(h==='"'||h==="'"){r++;let p=r;for(;r<s.length&&s[r]!==h;)r++;u=s.slice(p,r),r++}else{let p=r;for(;r<s.length&&/[^\s>]/.test(s[r]);)r++;u=s.slice(p,r)}i.push({name:c,value:u})}let a=!1;for(s[r]==="/"&&(a=!0,r++);r<s.length&&s[r]!==">";)r++;return{name:o,closing:e,selfClosing:a,attributes:i,end:r+1}}function vr(s,t){if(typeof s!="string")return null;let{banned:e,urlAttributes:r,isSafeUrl:n,rootTag:o,onTag:i}=t,a=(m,g)=>{let f=m.toLowerCase();return!(f.startsWith("on")||r.has(f)&&!n(g??""))},l=m=>{i&&i(m);let g=`<${m.name}`;for(let{name:f,value:b}of m.attributes)a(f,b)&&(g+=b===null?` ${f}`:` ${f}="${b.replace(/"/g,"&quot;")}"`);return`${g}${m.selfClosing?"/":""}>`},c="",d=0,h=0,u=!o,p=0;for(;p<s.length;){let m=s.indexOf("<",p);if(m===-1){u&&h===0&&(c+=s.slice(p));break}if(u&&h===0&&(c+=s.slice(p,m)),s.startsWith("<!--",m)){let f=s.indexOf("-->",m);p=f===-1?s.length:f+3;continue}if(s.startsWith("<![CDATA[",m)){let f=s.indexOf("]]>",m);p=f===-1?s.length:f+3;continue}if(s.startsWith("<!",m)||s.startsWith("<?",m)){let f=s.indexOf(">",m);p=f===-1?s.length:f+1;continue}let g=Gn(s,m);if(p=g.end,!u){if(g.name!==o||g.closing)continue;if(u=!0,d=1,c+=l(g),g.selfClosing)break;continue}if(h>0){g.closing?e.has(g.name)&&h--:e.has(g.name)&&!g.selfClosing&&h++;continue}if(g.closing){if(o&&g.name===o&&(d--,d===0)){c+=`</${o}>`;break}c+=`</${g.name}>`;continue}if(e.has(g.name)){g.selfClosing||h++;continue}o&&g.name===o&&d++,c+=l(g)}return u?c:null}var Kn=new Set(["script","foreignobject","iframe","embed","object","handler","annotation-xml"]),Yn=new Set(["href","xlink:href","src","from","to","values"]);function Zn(s){let t=br(s);return t.startsWith("#")?!0:!/^[a-z][a-z0-9+.-]*:/.test(t)}var yr=new Map;function _r(s){if(typeof s!="string")return null;let t=yr.get(s);if(t!==void 0)return t;let e=vr(s,{banned:Kn,urlAttributes:Yn,isSafeUrl:Zn,rootTag:"svg"});return yr.set(s,e),e}var xr=new Set;function Xn(s){xr.has(s)||(xr.add(s),console.warn(`[arc-icon] No icon named "${s}" in the active library. Check the spelling against the library in use, switch with iconRegistry.use("lucide"), or register it yourself with iconRegistry.set({ "`+s+'": "<svg\u2026>" }).'))}var $t=class extends D(C){constructor(){super(),this.name="",this.size="sm",this.label="",this._svgContent=null}willUpdate(t){let e=Number(this.size);t.has("size")&&this.size!==""&&Number.isFinite(e)&&e>0&&cr(this,{width:`${e}px`,height:`${e}px`})}updated(t){if(t.has("name")&&this._loadIcon(),t.has("size")){let e=Number(this.size);this.size!==""&&Number.isFinite(e)&&e>0?(this.style.width=`${e}px`,this.style.height=`${e}px`):(this.style.removeProperty("width"),this.style.removeProperty("height"))}}async _loadIcon(){if(!this.name){this._svgContent=null;return}let t=Xt.getSync(this.name);if(t!==null){this._svgContent=t;return}let e=this.name,r=await Xt.get(this.name);this.name===e&&(this._svgContent=r,r===null&&Xt.hasLibrary()&&Xn(e))}render(){let t=this._svgContent??Xt.getSync(this.name),e=t?_r(t):null;return w`
      <span
        class="icon"
        role=${this.label?"img":"presentation"}
        aria-label=${this.label||$}
        aria-hidden=${this.label?"false":"true"}
        part="base icon"
      >
        ${e?lr(e):w`<slot></slot>`}
      </span>
    `}};x($t,"properties",{name:{type:String,reflect:!0},size:{type:String,reflect:!0},label:{type:String},_svgContent:{state:!0}}),x($t,"styles",[L,A`
      :host {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: currentColor;
        vertical-align: middle;
      }

      :host([size="xs"]) { width: 12px; height: 12px; }
      :host(:not([size="lg"]):not([size="md"]):not([size="xl"]):not([size="xs"])),
      :host([size="sm"]) { width: 16px; height: 16px; }
      :host([size="md"]) { width: 20px; height: 20px; }
      :host([size="lg"]) { width: 24px; height: 24px; }
      :host([size="xl"]) { width: 32px; height: 32px; }
      /* Numeric sizes (px) are applied as inline width/height in updated() */

      .icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
      }

      svg {
        width: 100%;
        height: 100%;
      }

      ::slotted(svg) {
        width: 100%;
        height: 100%;
        fill: currentColor;
      }
    `]);customElements.get("arc-icon")||customElements.define("arc-icon",$t);$t[Symbol.for("tagName")]="arc-icon";customElements.get("arc-video")||customElements.define("arc-video",wt);wt[Symbol.for("tagName")]="arc-video";var it=class extends D(C){constructor(){super(),this._items=[],this._openItems=new Set}_onSlotChange(t){this._items=t.target.assignedElements({flatten:!0}).filter(e=>e.tagName==="ARC-ACCORDION-ITEM")}_toggle(t){let e=new Set(this._openItems);e.has(t)?e.delete(t):(this.multiple||e.clear(),e.add(t)),this._openItems=e}firstUpdated(){st(this)}render(){return w`
      <div part="base" class="accordion__slot-host">
        <slot @slotchange=${this._onSlotChange}></slot>
      </div>
      <div class="accordion" part="accordion">
        ${this._items.map((t,e)=>{let r=this._openItems.has(e);return w`
            <div class="accordion__item">
              <button
                class="accordion__trigger"
                id="accordion-trigger-${e}"
                aria-expanded=${r?"true":"false"}
                aria-controls="accordion-panel-${e}"
                @click=${()=>this._toggle(e)}
              >
                <span>${t.question}</span>
                <svg class="accordion__chevron" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <div
                class="accordion__content ${r?"is-open":""}"
                id="accordion-panel-${e}"
                role="region"
                aria-labelledby="accordion-trigger-${e}"
              >
                <div class="accordion__body">
                  <p>${t.answer}</p>
                </div>
              </div>
            </div>
          `})}
      </div>
    `}};x(it,"properties",{multiple:j(!1),_items:{state:!0},_openItems:{state:!0}}),x(it,"styles",[L,A`
      :host { display: block; }

      .accordion {
        display: flex;
        flex-direction: column;
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        overflow: hidden;
      }

      .accordion__item {
        background: var(--surface-raised);
        position: relative;
      }

      .accordion__item + .accordion__item::before {
        content: '';
        position: absolute;
        top: 0;
        inset-inline-start: var(--space-md);
        inset-inline-end: var(--space-md);
        height: 1px;
        background: var(--divider-glow);
        opacity: 0.4;
      }

      .accordion__trigger {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-md);
        width: 100%;
        padding: var(--space-lg);
        cursor: pointer;
        font-family: var(--font-body);
        font-size: var(--_text-md);
        font-weight: var(--font-label-weight, 600);
        color: var(--text-primary);
        background: none;
        border: none;
        text-align: start;
        transition: background var(--transition-fast), box-shadow var(--transition-fast), transform var(--duration-fast) var(--ease-out);
        min-height: var(--touch-min);
      }

      .accordion__trigger:hover {
        background: var(--surface-overlay);
        box-shadow: var(--interactive-hover);
      }
      .accordion__trigger:active { transform: scale(0.98); }
      .accordion__trigger[aria-expanded="true"] { background: var(--surface-overlay); }
      .accordion__trigger:focus-visible {
        outline: none;
        box-shadow: var(--interactive-focus-inset);
        background: var(--surface-overlay);
      }

      .accordion__chevron {
        color: var(--text-muted);
        width: 18px;
        height: 18px;
        transition: transform var(--duration-base) var(--ease-out);
        flex-shrink: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }

      .accordion__trigger[aria-expanded="true"] .accordion__chevron {
        transform: rotate(180deg);
      }

      .accordion__content {
        display: grid;
        grid-template-rows: 0fr;
        transition: grid-template-rows var(--transition-slow);
      }
      .accordion__content.is-open { grid-template-rows: 1fr; }

      .accordion__body { overflow: hidden; }

      .accordion__body p {
        color: var(--text-secondary);
        font-family: var(--font-body);
        font-size: var(--_text-sm);
        line-height: var(--body-lh);
        padding: var(--space-md);
        margin: 0;
      }

      .accordion__slot-host { display: none; }
    `]),x(it,"slotReaders",{"":"_onSlotChange"});var Mt=class extends C{constructor(){super(),this.question=""}get answer(){return this.textContent.trim()}render(){return w`<slot></slot>`}};x(Mt,"properties",{question:{type:String,reflect:!0}}),x(Mt,"styles",A`
    :host { display: none; }
  `);customElements.get("arc-accordion-item")||customElements.define("arc-accordion-item",Mt);Mt[Symbol.for("tagName")]="arc-accordion-item";customElements.get("arc-accordion")||customElements.define("arc-accordion",it);it[Symbol.for("tagName")]="arc-accordion";var ge=window,be=ge.ShadowRoot&&(ge.ShadyCSS===void 0||ge.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Ze=Symbol(),wr=new WeakMap,Jt=class{constructor(t,e,r){if(this._$cssResult$=!0,r!==Ze)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(be&&t===void 0){let r=e!==void 0&&e.length===1;r&&(t=wr.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),r&&wr.set(e,t))}return t}toString(){return this.cssText}},$r=s=>new Jt(typeof s=="string"?s:s+"",void 0,Ze),Qt=(s,...t)=>{let e=s.length===1?s[0]:t.reduce(((r,n,o)=>r+(i=>{if(i._$cssResult$===!0)return i.cssText;if(typeof i=="number")return i;throw Error("Value passed to 'css' function must be a 'css' function result: "+i+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(n)+s[o+1]),s[0]);return new Jt(e,s,Ze)},Xe=(s,t)=>{be?s.adoptedStyleSheets=t.map((e=>e instanceof CSSStyleSheet?e:e.styleSheet)):t.forEach((e=>{let r=document.createElement("style"),n=ge.litNonce;n!==void 0&&r.setAttribute("nonce",n),r.textContent=e.cssText,s.appendChild(r)}))},ve=be?s=>s:s=>s instanceof CSSStyleSheet?(t=>{let e="";for(let r of t.cssRules)e+=r.cssText;return $r(e)})(s):s;var Je,ye=window,Mr=ye.trustedTypes,Jn=Mr?Mr.emptyScript:"",kr=ye.reactiveElementPolyfillSupport,ts={toAttribute(s,t){switch(t){case Boolean:s=s?Jn:null;break;case Object:case Array:s=s==null?s:JSON.stringify(s)}return s},fromAttribute(s,t){let e=s;switch(t){case Boolean:e=s!==null;break;case Number:e=s===null?null:Number(s);break;case Object:case Array:try{e=JSON.parse(s)}catch{e=null}}return e}},Sr=(s,t)=>t!==s&&(t==t||s==s),Qe={attribute:!0,type:String,converter:ts,reflect:!1,hasChanged:Sr},es="finalized",Z=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),((e=this.h)!==null&&e!==void 0?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();let t=[];return this.elementProperties.forEach(((e,r)=>{let n=this._$Ep(r,e);n!==void 0&&(this._$Ev.set(n,r),t.push(n))})),t}static createProperty(t,e=Qe){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){let r=typeof t=="symbol"?Symbol():"__"+t,n=this.getPropertyDescriptor(t,r,e);n!==void 0&&Object.defineProperty(this.prototype,t,n)}}static getPropertyDescriptor(t,e,r){return{get(){return this[e]},set(n){let o=this[t];this[e]=n,this.requestUpdate(t,o,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Qe}static finalize(){if(this.hasOwnProperty(es))return!1;this[es]=!0;let t=Object.getPrototypeOf(this);if(t.finalize(),t.h!==void 0&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){let e=this.properties,r=[...Object.getOwnPropertyNames(e),...Object.getOwnPropertySymbols(e)];for(let n of r)this.createProperty(n,e[n])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let r=new Set(t.flat(1/0).reverse());for(let n of r)e.unshift(ve(n))}else t!==void 0&&e.push(ve(t));return e}static _$Ep(t,e){let r=e.attribute;return r===!1?void 0:typeof r=="string"?r:typeof t=="string"?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise((e=>this.enableUpdating=e)),this._$AL=new Map,this._$Eg(),this.requestUpdate(),(t=this.constructor.h)===null||t===void 0||t.forEach((e=>e(this)))}addController(t){var e,r;((e=this._$ES)!==null&&e!==void 0?e:this._$ES=[]).push(t),this.renderRoot!==void 0&&this.isConnected&&((r=t.hostConnected)===null||r===void 0||r.call(t))}removeController(t){var e;(e=this._$ES)===null||e===void 0||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;let e=(t=this.shadowRoot)!==null&&t!==void 0?t:this.attachShadow(this.constructor.shadowRootOptions);return Xe(e,this.constructor.elementStyles),e}connectedCallback(){var t;this.renderRoot===void 0&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),(t=this._$ES)===null||t===void 0||t.forEach((e=>{var r;return(r=e.hostConnected)===null||r===void 0?void 0:r.call(e)}))}enableUpdating(t){}disconnectedCallback(){var t;(t=this._$ES)===null||t===void 0||t.forEach((e=>{var r;return(r=e.hostDisconnected)===null||r===void 0?void 0:r.call(e)}))}attributeChangedCallback(t,e,r){this._$AK(t,r)}_$EO(t,e,r=Qe){var n;let o=this.constructor._$Ep(t,r);if(o!==void 0&&r.reflect===!0){let i=(((n=r.converter)===null||n===void 0?void 0:n.toAttribute)!==void 0?r.converter:ts).toAttribute(e,r.type);this._$El=t,i==null?this.removeAttribute(o):this.setAttribute(o,i),this._$El=null}}_$AK(t,e){var r;let n=this.constructor,o=n._$Ev.get(t);if(o!==void 0&&this._$El!==o){let i=n.getPropertyOptions(o),a=typeof i.converter=="function"?{fromAttribute:i.converter}:((r=i.converter)===null||r===void 0?void 0:r.fromAttribute)!==void 0?i.converter:ts;this._$El=o,this[o]=a.fromAttribute(e,i.type),this._$El=null}}requestUpdate(t,e,r){let n=!0;t!==void 0&&(((r=r||this.constructor.getPropertyOptions(t)).hasChanged||Sr)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),r.reflect===!0&&this._$El!==t&&(this._$EC===void 0&&(this._$EC=new Map),this._$EC.set(t,r))):n=!1),!this.isUpdatePending&&n&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach(((n,o)=>this[o]=n)),this._$Ei=void 0);let e=!1,r=this._$AL;try{e=this.shouldUpdate(r),e?(this.willUpdate(r),(t=this._$ES)===null||t===void 0||t.forEach((n=>{var o;return(o=n.hostUpdate)===null||o===void 0?void 0:o.call(n)})),this.update(r)):this._$Ek()}catch(n){throw e=!1,this._$Ek(),n}e&&this._$AE(r)}willUpdate(t){}_$AE(t){var e;(e=this._$ES)===null||e===void 0||e.forEach((r=>{var n;return(n=r.hostUpdated)===null||n===void 0?void 0:n.call(r)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){this._$EC!==void 0&&(this._$EC.forEach(((e,r)=>this._$EO(r,this[r],e))),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};Z[es]=!0,Z.elementProperties=new Map,Z.elementStyles=[],Z.shadowRootOptions={mode:"open"},kr?.({ReactiveElement:Z}),((Je=ye.reactiveElementVersions)!==null&&Je!==void 0?Je:ye.reactiveElementVersions=[]).push("1.6.3");var ss,_e=window,Lt=_e.trustedTypes,Ar=Lt?Lt.createPolicy("lit-html",{createHTML:s=>s}):void 0,ns="$lit$",at=`lit$${(Math.random()+"").slice(9)}$`,Tr="?"+at,Qn=`<${Tr}>`,At=document,ee=()=>At.createComment(""),se=s=>s===null||typeof s!="object"&&typeof s!="function",Nr=Array.isArray,to=s=>Nr(s)||typeof s?.[Symbol.iterator]=="function",rs=`[ 	
\f\r]`,te=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Er=/-->/g,Cr=/>/g,kt=RegExp(`>|${rs}(?:([^\\s"'>=/]+)(${rs}*=${rs}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),Pr=/'/g,zr=/"/g,Lr=/^(?:script|style|textarea|title)$/i,Dr=s=>(t,...e)=>({_$litType$:s,strings:t,values:e}),Ir=Dr(1),jl=Dr(2),Et=Symbol.for("lit-noChange"),I=Symbol.for("lit-nothing"),Rr=new WeakMap,St=At.createTreeWalker(At,129,null,!1);function Ur(s,t){if(!Array.isArray(s)||!s.hasOwnProperty("raw"))throw Error("invalid template strings array");return Ar!==void 0?Ar.createHTML(t):t}var eo=(s,t)=>{let e=s.length-1,r=[],n,o=t===2?"<svg>":"",i=te;for(let a=0;a<e;a++){let l=s[a],c,d,h=-1,u=0;for(;u<l.length&&(i.lastIndex=u,d=i.exec(l),d!==null);)u=i.lastIndex,i===te?d[1]==="!--"?i=Er:d[1]!==void 0?i=Cr:d[2]!==void 0?(Lr.test(d[2])&&(n=RegExp("</"+d[2],"g")),i=kt):d[3]!==void 0&&(i=kt):i===kt?d[0]===">"?(i=n??te,h=-1):d[1]===void 0?h=-2:(h=i.lastIndex-d[2].length,c=d[1],i=d[3]===void 0?kt:d[3]==='"'?zr:Pr):i===zr||i===Pr?i=kt:i===Er||i===Cr?i=te:(i=kt,n=void 0);let p=i===kt&&s[a+1].startsWith("/>")?" ":"";o+=i===te?l+Qn:h>=0?(r.push(c),l.slice(0,h)+ns+l.slice(h)+at+p):l+at+(h===-2?(r.push(void 0),a):p)}return[Ur(s,o+(s[e]||"<?>")+(t===2?"</svg>":"")),r]},re=class s{constructor({strings:t,_$litType$:e},r){let n;this.parts=[];let o=0,i=0,a=t.length-1,l=this.parts,[c,d]=eo(t,e);if(this.el=s.createElement(c,r),St.currentNode=this.el.content,e===2){let h=this.el.content,u=h.firstChild;u.remove(),h.append(...u.childNodes)}for(;(n=St.nextNode())!==null&&l.length<a;){if(n.nodeType===1){if(n.hasAttributes()){let h=[];for(let u of n.getAttributeNames())if(u.endsWith(ns)||u.startsWith(at)){let p=d[i++];if(h.push(u),p!==void 0){let m=n.getAttribute(p.toLowerCase()+ns).split(at),g=/([.?@])?(.*)/.exec(p);l.push({type:1,index:o,name:g[2],strings:m,ctor:g[1]==="."?is:g[1]==="?"?as:g[1]==="@"?ls:It})}else l.push({type:6,index:o})}for(let u of h)n.removeAttribute(u)}if(Lr.test(n.tagName)){let h=n.textContent.split(at),u=h.length-1;if(u>0){n.textContent=Lt?Lt.emptyScript:"";for(let p=0;p<u;p++)n.append(h[p],ee()),St.nextNode(),l.push({type:2,index:++o});n.append(h[u],ee())}}}else if(n.nodeType===8)if(n.data===Tr)l.push({type:2,index:o});else{let h=-1;for(;(h=n.data.indexOf(at,h+1))!==-1;)l.push({type:7,index:o}),h+=at.length-1}o++}}static createElement(t,e){let r=At.createElement("template");return r.innerHTML=t,r}};function Dt(s,t,e=s,r){var n,o,i,a;if(t===Et)return t;let l=r!==void 0?(n=e._$Co)===null||n===void 0?void 0:n[r]:e._$Cl,c=se(t)?void 0:t._$litDirective$;return l?.constructor!==c&&((o=l?._$AO)===null||o===void 0||o.call(l,!1),c===void 0?l=void 0:(l=new c(s),l._$AT(s,e,r)),r!==void 0?((i=(a=e)._$Co)!==null&&i!==void 0?i:a._$Co=[])[r]=l:e._$Cl=l),l!==void 0&&(t=Dt(s,l._$AS(s,t.values),l,r)),t}var os=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;let{el:{content:r},parts:n}=this._$AD,o=((e=t?.creationScope)!==null&&e!==void 0?e:At).importNode(r,!0);St.currentNode=o;let i=St.nextNode(),a=0,l=0,c=n[0];for(;c!==void 0;){if(a===c.index){let d;c.type===2?d=new ne(i,i.nextSibling,this,t):c.type===1?d=new c.ctor(i,c.name,c.strings,this,t):c.type===6&&(d=new cs(i,this,t)),this._$AV.push(d),c=n[++l]}a!==c?.index&&(i=St.nextNode(),a++)}return St.currentNode=At,o}v(t){let e=0;for(let r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(t,r,e),e+=r.strings.length-2):r._$AI(t[e])),e++}},ne=class s{constructor(t,e,r,n){var o;this.type=2,this._$AH=I,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=r,this.options=n,this._$Cp=(o=n?.isConnected)===null||o===void 0||o}get _$AU(){var t,e;return(e=(t=this._$AM)===null||t===void 0?void 0:t._$AU)!==null&&e!==void 0?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Dt(this,t,e),se(t)?t===I||t==null||t===""?(this._$AH!==I&&this._$AR(),this._$AH=I):t!==this._$AH&&t!==Et&&this._(t):t._$litType$!==void 0?this.g(t):t.nodeType!==void 0?this.$(t):to(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==I&&se(this._$AH)?this._$AA.nextSibling.data=t:this.$(At.createTextNode(t)),this._$AH=t}g(t){var e;let{values:r,_$litType$:n}=t,o=typeof n=="number"?this._$AC(t):(n.el===void 0&&(n.el=re.createElement(Ur(n.h,n.h[0]),this.options)),n);if(((e=this._$AH)===null||e===void 0?void 0:e._$AD)===o)this._$AH.v(r);else{let i=new os(o,this),a=i.u(this.options);i.v(r),this.$(a),this._$AH=i}}_$AC(t){let e=Rr.get(t.strings);return e===void 0&&Rr.set(t.strings,e=new re(t)),e}T(t){Nr(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,r,n=0;for(let o of t)n===e.length?e.push(r=new s(this.k(ee()),this.k(ee()),this,this.options)):r=e[n],r._$AI(o),n++;n<e.length&&(this._$AR(r&&r._$AB.nextSibling,n),e.length=n)}_$AR(t=this._$AA.nextSibling,e){var r;for((r=this._$AP)===null||r===void 0||r.call(this,!1,!0,e);t&&t!==this._$AB;){let n=t.nextSibling;t.remove(),t=n}}setConnected(t){var e;this._$AM===void 0&&(this._$Cp=t,(e=this._$AP)===null||e===void 0||e.call(this,t))}},It=class{constructor(t,e,r,n,o){this.type=1,this._$AH=I,this._$AN=void 0,this.element=t,this.name=e,this._$AM=n,this.options=o,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=I}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,r,n){let o=this.strings,i=!1;if(o===void 0)t=Dt(this,t,e,0),i=!se(t)||t!==this._$AH&&t!==Et,i&&(this._$AH=t);else{let a=t,l,c;for(t=o[0],l=0;l<o.length-1;l++)c=Dt(this,a[r+l],e,l),c===Et&&(c=this._$AH[l]),i||(i=!se(c)||c!==this._$AH[l]),c===I?t=I:t!==I&&(t+=(c??"")+o[l+1]),this._$AH[l]=c}i&&!n&&this.j(t)}j(t){t===I?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},is=class extends It{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===I?void 0:t}},so=Lt?Lt.emptyScript:"",as=class extends It{constructor(){super(...arguments),this.type=4}j(t){t&&t!==I?this.element.setAttribute(this.name,so):this.element.removeAttribute(this.name)}},ls=class extends It{constructor(t,e,r,n,o){super(t,e,r,n,o),this.type=5}_$AI(t,e=this){var r;if((t=(r=Dt(this,t,e,0))!==null&&r!==void 0?r:I)===Et)return;let n=this._$AH,o=t===I&&n!==I||t.capture!==n.capture||t.once!==n.once||t.passive!==n.passive,i=t!==I&&(n===I||o);o&&this.element.removeEventListener(this.name,this,n),i&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,r;typeof this._$AH=="function"?this._$AH.call((r=(e=this.options)===null||e===void 0?void 0:e.host)!==null&&r!==void 0?r:this.element,t):this._$AH.handleEvent(t)}},cs=class{constructor(t,e,r){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(t){Dt(this,t)}};var Or=_e.litHtmlPolyfillSupport;Or?.(re,ne),((ss=_e.litHtmlVersions)!==null&&ss!==void 0?ss:_e.litHtmlVersions=[]).push("2.8.0");var qr=(s,t,e)=>{var r,n;let o=(r=e?.renderBefore)!==null&&r!==void 0?r:t,i=o._$litPart$;if(i===void 0){let a=(n=e?.renderBefore)!==null&&n!==void 0?n:null;o._$litPart$=i=new ne(t.insertBefore(ee(),a),a,void 0,e??{})}return i._$AI(s),i};var hs,ds;var lt=class extends Z{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;let r=super.createRenderRoot();return(t=(e=this.renderOptions).renderBefore)!==null&&t!==void 0||(e.renderBefore=r.firstChild),r}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=qr(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),(t=this._$Do)===null||t===void 0||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),(t=this._$Do)===null||t===void 0||t.setConnected(!1)}render(){return Et}};lt.finalized=!0,lt._$litElement$=!0,(hs=globalThis.litElementHydrateSupport)===null||hs===void 0||hs.call(globalThis,{LitElement:lt});var Hr=globalThis.litElementPolyfillSupport;Hr?.({LitElement:lt});((ds=globalThis.litElementVersions)!==null&&ds!==void 0?ds:globalThis.litElementVersions=[]).push("3.3.3");var jr=s=>t=>typeof t=="function"?((e,r)=>(customElements.define(e,r),r))(s,t):((e,r)=>{let{kind:n,elements:o}=r;return{kind:n,elements:o,finisher(i){customElements.define(e,i)}}})(s,t);var ro=(s,t)=>t.kind==="method"&&t.descriptor&&!("value"in t.descriptor)?{...t,finisher(e){e.createProperty(t.key,s)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:t.key,initializer(){typeof t.initializer=="function"&&(this[t.key]=t.initializer.call(this))},finisher(e){e.createProperty(t.key,s)}},no=(s,t,e)=>{t.constructor.createProperty(e,s)};function xe(s){return(t,e)=>e!==void 0?no(s,t,e):ro(s,t)}var Ct=({finisher:s,descriptor:t})=>(e,r)=>{var n;if(r===void 0){let o=(n=e.originalKey)!==null&&n!==void 0?n:e.key,i=t!=null?{kind:"method",placement:"prototype",key:o,descriptor:t(e.key)}:{...e,key:o};return s!=null&&(i.finisher=function(a){s(a,o)}),i}{let o=e.constructor;t!==void 0&&Object.defineProperty(e,r,t(r)),s?.(o,r)}};function Br(s,t){return Ct({descriptor:e=>{let r={get(){var n,o;return(o=(n=this.renderRoot)===null||n===void 0?void 0:n.querySelector(s))!==null&&o!==void 0?o:null},enumerable:!0,configurable:!0};if(t){let n=typeof e=="symbol"?Symbol():"__"+e;r.get=function(){var o,i;return this[n]===void 0&&(this[n]=(i=(o=this.renderRoot)===null||o===void 0?void 0:o.querySelector(s))!==null&&i!==void 0?i:null),this[n]}}return r}})}var us,mc=((us=window.HTMLSlotElement)===null||us===void 0?void 0:us.prototype.assignedElements)!=null?(s,t)=>s.assignedElements(t):(s,t)=>s.assignedNodes(t).filter((e=>e.nodeType===Node.ELEMENT_NODE));var oo=function(s,t,e,r){var n=arguments.length,o=n<3?t:r===null?r=Object.getOwnPropertyDescriptor(t,e):r,i;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")o=Reflect.decorate(s,t,e,r);else for(var a=s.length-1;a>=0;a--)(i=s[a])&&(o=(n<3?i(o):n>3?i(t,e,o):i(t,e))||o);return n>3&&o&&Object.defineProperty(t,e,o),o},io=function(s,t){if(typeof Reflect=="object"&&typeof Reflect.metadata=="function")return Reflect.metadata(s,t)},Fr=Qt`
:host {
  opacity: 0;
}
:host(.wired-rendered) {
  opacity: 1;
}
#overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}
svg {
  display: block;
}
path {
  stroke: currentColor;
  stroke-width: 0.7;
  fill: transparent;
}
.hidden {
  display: none !important;
}
`,oe=class extends lt{constructor(){super(...arguments),this.lastSize=[0,0],this.seed=Math.floor(Math.random()*2**31)}updated(t){this.wiredRender()}wiredRender(t=!1){if(this.svg){let e=this.canvasSize();if(!t&&e[0]===this.lastSize[0]&&e[1]===this.lastSize[1])return;for(;this.svg.hasChildNodes();)this.svg.removeChild(this.svg.lastChild);this.svg.setAttribute("width",`${e[0]}`),this.svg.setAttribute("height",`${e[1]}`),this.draw(this.svg,e),this.lastSize=e,this.classList.add("wired-rendered")}}fire(t,e){ao(this,t,e)}};oo([Br("svg"),io("design:type",SVGSVGElement)],oe.prototype,"svg",void 0);function ao(s,t,e){s.dispatchEvent(new CustomEvent(t,{composed:!0,bubbles:!0,detail:e}))}function ps(s,t,e){if(s&&s.length){let[r,n]=t,o=Math.PI/180*e,i=Math.cos(o),a=Math.sin(o);for(let l of s){let[c,d]=l;l[0]=(c-r)*i-(d-n)*a+r,l[1]=(c-r)*a+(d-n)*i+n}}}function lo(s,t,e){let r=[];s.forEach(n=>r.push(...n)),ps(r,t,e)}function co(s,t){return s[0]===t[0]&&s[1]===t[1]}function Vr(s,t,e,r=1){let n=e,o=Math.max(t,.1),i=s[0]&&s[0][0]&&typeof s[0][0]=="number"?[s]:s,a=[0,0];if(n)for(let c of i)ps(c,a,n);let l=ho(i,o,r);if(n){for(let c of i)ps(c,a,-n);lo(l,a,-n)}return l}function ho(s,t,e){let r=[];for(let c of s){let d=[...c];co(d[0],d[d.length-1])||d.push([d[0][0],d[0][1]]),d.length>2&&r.push(d)}let n=[];t=Math.max(t,.1);let o=[];for(let c of r)for(let d=0;d<c.length-1;d++){let h=c[d],u=c[d+1];if(h[1]!==u[1]){let p=Math.min(h[1],u[1]);o.push({ymin:p,ymax:Math.max(h[1],u[1]),x:p===h[1]?h[0]:u[0],islope:(u[0]-h[0])/(u[1]-h[1])})}}if(o.sort((c,d)=>c.ymin<d.ymin?-1:c.ymin>d.ymin?1:c.x<d.x?-1:c.x>d.x?1:c.ymax===d.ymax?0:(c.ymax-d.ymax)/Math.abs(c.ymax-d.ymax)),!o.length)return n;let i=[],a=o[0].ymin,l=0;for(;i.length||o.length;){if(o.length){let c=-1;for(let h=0;h<o.length&&!(o[h].ymin>a);h++)c=h;o.splice(0,c+1).forEach(h=>{i.push({s:a,edge:h})})}if(i=i.filter(c=>!(c.edge.ymax<=a)),i.sort((c,d)=>c.edge.x===d.edge.x?0:(c.edge.x-d.edge.x)/Math.abs(c.edge.x-d.edge.x)),(e!==1||l%t===0)&&i.length>1)for(let c=0;c<i.length;c=c+2){let d=c+1;if(d>=i.length)break;let h=i[c].edge,u=i[d].edge;n.push([[Math.round(h.x),a],[Math.round(u.x),a]])}a+=e,i.forEach(c=>{c.edge.x=c.edge.x+e*c.edge.islope}),l++}return n}function Pt(s,t){var e;let r=t.hachureAngle+90,n=t.hachureGap;n<0&&(n=t.strokeWidth*4),n=Math.round(Math.max(n,.1));let o=1;return t.roughness>=1&&(((e=t.randomizer)===null||e===void 0?void 0:e.next())||Math.random())>.7&&(o=n),Vr(s,n,r,o||1)}var Ut=class{constructor(t){this.helper=t}fillPolygons(t,e){return this._fillPolygons(t,e)}_fillPolygons(t,e){let r=Pt(t,e);return{type:"fillSketch",ops:this.renderLines(r,e)}}renderLines(t,e){let r=[];for(let n of t)r.push(...this.helper.doubleLineOps(n[0][0],n[0][1],n[1][0],n[1][1],e));return r}};function ie(s){let t=s[0],e=s[1];return Math.sqrt(Math.pow(t[0]-e[0],2)+Math.pow(t[1]-e[1],2))}var ae=class extends Ut{fillPolygons(t,e){let r=e.hachureGap;r<0&&(r=e.strokeWidth*4),r=Math.max(r,.1);let n=Object.assign({},e,{hachureGap:r}),o=Pt(t,n),i=Math.PI/180*e.hachureAngle,a=[],l=r*.5*Math.cos(i),c=r*.5*Math.sin(i);for(let[h,u]of o)ie([h,u])&&a.push([[h[0]-l,h[1]+c],[...u]],[[h[0]+l,h[1]-c],[...u]]);return{type:"fillSketch",ops:this.renderLines(a,e)}}};var we=class{constructor(t){this.seed=t}next(){return this.seed?(2**31-1&(this.seed=Math.imul(48271,this.seed)))/2**31:Math.random()}};function gs(s,t,e,r,n){return{type:"path",ops:$e(s,t,e,r,n)}}function mo(s,t,e){let r=(s||[]).length;if(r>2){let n=[];for(let o=0;o<r-1;o++)n.push(...$e(s[o][0],s[o][1],s[o+1][0],s[o+1][1],e));return t&&n.push(...$e(s[r-1][0],s[r-1][1],s[0][0],s[0][1],e)),{type:"path",ops:n}}else if(r===2)return gs(s[0][0],s[0][1],s[1][0],s[1][1],e);return{type:"path",ops:[]}}function Kr(s,t){return mo(s,!0,t)}function Yr(s,t,e,r,n){let o=[[s,t],[s+e,t],[s+e,t+r],[s,t+r]];return Kr(o,n)}function Zr(s,t,e,r,n){let o=Xr(e,r,n);return go(s,t,n,o).opset}function Xr(s,t,e){let r=Math.sqrt(Math.PI*2*Math.sqrt((Math.pow(s/2,2)+Math.pow(t/2,2))/2)),n=Math.ceil(Math.max(e.curveStepCount,e.curveStepCount/Math.sqrt(200)*r)),o=Math.PI*2/n,i=Math.abs(s/2),a=Math.abs(t/2),l=1-e.curveFitting;return i+=T(i*l,e),a+=T(a*l,e),{increment:o,rx:i,ry:a}}function go(s,t,e,r){let[n,o]=Gr(r.increment,s,t,r.rx,r.ry,1,r.increment*fs(.1,fs(.4,1,e),e),e),i=Wr(n,null,e);if(!e.disableMultiStroke&&e.roughness!==0){let[a]=Gr(r.increment,s,t,r.rx,r.ry,1.5,0,e),l=Wr(a,null,e);i=i.concat(l)}return{estimatedPoints:o,opset:{type:"path",ops:i}}}function Jr(s,t,e,r,n){return $e(s,t,e,r,n,!0)}function Qr(s){return s.randomizer||(s.randomizer=new we(s.seed||0)),s.randomizer.next()}function fs(s,t,e,r=1){return e.roughness*r*(Qr(e)*(t-s)+s)}function T(s,t,e=1){return fs(-s,s,t,e)}function $e(s,t,e,r,n,o=!1){let i=o?n.disableMultiStrokeFill:n.disableMultiStroke,a=ms(s,t,e,r,n,!0,!1);if(i)return a;let l=ms(s,t,e,r,n,!0,!0);return a.concat(l)}function ms(s,t,e,r,n,o,i){let a=Math.pow(s-e,2)+Math.pow(t-r,2),l=Math.sqrt(a),c=1;l<200?c=1:l>500?c=.4:c=-.0016668*l+1.233334;let d=n.maxRandomnessOffset||0;d*d*100>a&&(d=l/10);let h=d/2,u=.2+Qr(n)*.2,p=n.bowing*n.maxRandomnessOffset*(r-t)/200,m=n.bowing*n.maxRandomnessOffset*(s-e)/200;p=T(p,n,c),m=T(m,n,c);let g=[],f=()=>T(h,n,c),b=()=>T(d,n,c),v=n.preserveVertices;return o&&(i?g.push({op:"move",data:[s+(v?0:f()),t+(v?0:f())]}):g.push({op:"move",data:[s+(v?0:T(d,n,c)),t+(v?0:T(d,n,c))]})),i?g.push({op:"bcurveTo",data:[p+s+(e-s)*u+f(),m+t+(r-t)*u+f(),p+s+2*(e-s)*u+f(),m+t+2*(r-t)*u+f(),e+(v?0:f()),r+(v?0:f())]}):g.push({op:"bcurveTo",data:[p+s+(e-s)*u+b(),m+t+(r-t)*u+b(),p+s+2*(e-s)*u+b(),m+t+2*(r-t)*u+b(),e+(v?0:b()),r+(v?0:b())]}),g}function Wr(s,t,e){let r=s.length,n=[];if(r>3){let o=[],i=1-e.curveTightness;n.push({op:"move",data:[s[1][0],s[1][1]]});for(let a=1;a+2<r;a++){let l=s[a];o[0]=[l[0],l[1]],o[1]=[l[0]+(i*s[a+1][0]-i*s[a-1][0])/6,l[1]+(i*s[a+1][1]-i*s[a-1][1])/6],o[2]=[s[a+1][0]+(i*s[a][0]-i*s[a+2][0])/6,s[a+1][1]+(i*s[a][1]-i*s[a+2][1])/6],o[3]=[s[a+1][0],s[a+1][1]],n.push({op:"bcurveTo",data:[o[1][0],o[1][1],o[2][0],o[2][1],o[3][0],o[3][1]]})}if(t&&t.length===2){let a=e.maxRandomnessOffset;n.push({op:"lineTo",data:[t[0]+T(a,e),t[1]+T(a,e)]})}}else r===3?(n.push({op:"move",data:[s[1][0],s[1][1]]}),n.push({op:"bcurveTo",data:[s[1][0],s[1][1],s[2][0],s[2][1],s[2][0],s[2][1]]})):r===2&&n.push(...ms(s[0][0],s[0][1],s[1][0],s[1][1],e,!0,!0));return n}function Gr(s,t,e,r,n,o,i,a){let l=a.roughness===0,c=[],d=[];if(l){s=s/4,d.push([t+r*Math.cos(-s),e+n*Math.sin(-s)]);for(let h=0;h<=Math.PI*2;h=h+s){let u=[t+r*Math.cos(h),e+n*Math.sin(h)];c.push(u),d.push(u)}d.push([t+r*Math.cos(0),e+n*Math.sin(0)]),d.push([t+r*Math.cos(s),e+n*Math.sin(s)])}else{let h=T(.5,a)-Math.PI/2;d.push([T(o,a)+t+.9*r*Math.cos(h-s),T(o,a)+e+.9*n*Math.sin(h-s)]);let u=Math.PI*2+h-.01;for(let p=h;p<u;p=p+s){let m=[T(o,a)+t+r*Math.cos(p),T(o,a)+e+n*Math.sin(p)];c.push(m),d.push(m)}d.push([T(o,a)+t+r*Math.cos(h+Math.PI*2+i*.5),T(o,a)+e+n*Math.sin(h+Math.PI*2+i*.5)]),d.push([T(o,a)+t+.98*r*Math.cos(h+i),T(o,a)+e+.98*n*Math.sin(h+i)]),d.push([T(o,a)+t+.9*r*Math.cos(h+i*.5),T(o,a)+e+.9*n*Math.sin(h+i*.5)])}return[d,c]}var bo={randOffset(s,t){return s},randOffsetWithRange(s,t,e){return(s+t)/2},ellipse(s,t,e,r,n){return Zr(s,t,e,r,n)},doubleLineOps(s,t,e,r,n){return Jr(s,t,e,r,n)}};function bs(s){return{maxRandomnessOffset:2,roughness:1,bowing:.85,stroke:"#000",strokeWidth:1.5,curveTightness:0,curveFitting:.95,curveStepCount:9,fillStyle:"hachure",fillWeight:3.5,hachureAngle:-41,hachureGap:5,dashOffset:-1,dashGap:-1,zigzagOffset:0,combineNestedSvgPaths:!1,disableMultiStroke:!1,disableMultiStrokeFill:!1,seed:s}}function vo(s,t){let e="";for(let r of s.ops){let n=r.data;switch(r.op){case"move":if(t&&e)break;e+=`M${n[0]} ${n[1]} `;break;case"bcurveTo":e+=`C${n[0]} ${n[1]}, ${n[2]} ${n[3]}, ${n[4]} ${n[5]} `;break;case"lineTo":e+=`L${n[0]} ${n[1]} `;break}}return e.trim()}function yo(s,t){let e=document.createElementNS("http://www.w3.org/2000/svg",s);if(t)for(let r in t)e.setAttributeNS(null,r,t[r]);return e}function vs(s,t,e=!1){let r=yo("path",{d:vo(s,e)});return t&&t.appendChild(r),r}function tn(s,t,e,r,n,o){return vs(Yr(t+2,e+2,r-4,n-4,bs(o)),s)}function le(s,t,e,r,n,o){return vs(gs(t,e,r,n,bs(o)),s)}function en(s,t){let r=new ae(bo).fillPolygon(s,bs(t));return vs(r,null)}var ys=function(s,t,e,r){var n=arguments.length,o=n<3?t:r===null?r=Object.getOwnPropertyDescriptor(t,e):r,i;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")o=Reflect.decorate(s,t,e,r);else for(var a=s.length-1;a>=0;a--)(i=s[a])&&(o=(n<3?i(o):n>3?i(t,e,o):i(t,e))||o);return n>3&&o&&Object.defineProperty(t,e,o),o},_s=function(s,t){if(typeof Reflect=="object"&&typeof Reflect.metadata=="function")return Reflect.metadata(s,t)},Me=class extends oe{constructor(){super(),this.elevation=1,this.roAttached=!1,window.ResizeObserver&&(this.resizeObserver=new window.ResizeObserver(()=>{this.svg&&this.wiredRender()}))}static get styles(){return[Fr,Qt`
        :host {
          display: inline-block;
          position: relative;
          padding: 10px;
        }
        path.cardFill {
          stroke-width: 3.5;
          stroke: var(--wired-card-background-fill);
        }
        path {
          stroke: var(--wired-card-background-fill, currentColor);
        }
      `]}render(){return Ir`
    <div id="overlay"><svg></svg></div>
    <div style="position: relative;">
      <slot @slotchange="${this.wiredRender}"></slot>
    </div>
    `}updated(t){let e=t.has("fill");this.wiredRender(e),this.attachResizeListener()}disconnectedCallback(){this.detachResizeListener()}attachResizeListener(){this.roAttached||(this.resizeObserver?this.resizeObserver.observe(this):this.windowResizeHandler||(this.windowResizeHandler=()=>this.wiredRender(),window.addEventListener("resize",this.windowResizeHandler,{passive:!0})),this.roAttached=!0)}detachResizeListener(){this.resizeObserver&&this.resizeObserver.unobserve(this),this.windowResizeHandler&&window.removeEventListener("resize",this.windowResizeHandler),this.roAttached=!1}canvasSize(){let t=this.getBoundingClientRect(),e=Math.min(Math.max(1,this.elevation),5),r=t.width+(e-1)*2,n=t.height+(e-1)*2;return[r,n]}draw(t,e){let r=Math.min(Math.max(1,this.elevation),5),n={width:e[0]-(r-1)*2,height:e[1]-(r-1)*2};if(this.fill&&this.fill.trim()){let o=en([[2,2],[n.width-4,2],[n.width-2,n.height-4],[2,n.height-4]],this.seed);o.classList.add("cardFill"),t.style.setProperty("--wired-card-background-fill",this.fill.trim()),t.appendChild(o)}tn(t,2,2,n.width-4,n.height-4,this.seed);for(let o=1;o<r;o++)le(t,o*2,n.height-4+o*2,n.width-4+o*2,n.height-4+o*2,this.seed).style.opacity=`${(85-o*10)/100}`,le(t,n.width-4+o*2,n.height-4+o*2,n.width-4+o*2,o*2,this.seed).style.opacity=`${(85-o*10)/100}`,le(t,o*2,n.height-4+o*2,n.width-4+o*2,n.height-4+o*2,this.seed).style.opacity=`${(85-o*10)/100}`,le(t,n.width-4+o*2,n.height-4+o*2,n.width-4+o*2,o*2,this.seed).style.opacity=`${(85-o*10)/100}`}};ys([xe({type:Number}),_s("design:type",Object)],Me.prototype,"elevation",void 0);ys([xe({type:String}),_s("design:type",String)],Me.prototype,"fill",void 0);Me=ys([jr("wired-card"),_s("design:paramtypes",[])],Me);function xs(s,t,e){return s+(t-s)*e}function nn(s){return s-Math.floor(s)}function ws(s,t){let e=Math.floor(s),r=Math.floor(t),n=s-e,o=t-r;n=n*n*(3-2*n),o=o*o*(3-2*o);let i=B(e,r),a=B(e+1,r),l=B(e,r+1),c=B(e+1,r+1);return i+(a-i)*n+(l-i)*o+(i-a-l+c)*n*o}function B(s,t){let e=Math.sin(s*12.9898+t*78.233)*43758.5453;return e-Math.floor(e)}function ks(s,t){let e=Math.PI*(3-Math.sqrt(5)),r=1-2*(s+.5)/t,n=Math.sqrt(1-r*r),o=s*e;return[n*Math.cos(o),r,n*Math.sin(o)]}function _o(s,t){return Math.atan2(Math.sin(s-t),Math.cos(s-t))}function ct(s,t,e,r,n){let o=Math.sin(t),i=Math.cos(t),a=Math.sin(s),l=Math.cos(s);return(c,d,h)=>{let u=c*l+h*a,p=-c*a+h*l,m=d*i-p*o,g=d*o+p*i;return[e+u*n,r-m*n,g]}}function on(s,t,e,r){if(!r){let o=Math.round((e?1-s:s)*255);return`rgba(${o},${o},${o},${t})`}let n=o=>Math.round(e?o*(1-s):o+(255-o)*s);return`rgba(${n(r.r)},${n(r.g)},${n(r.b)},${t})`}function an(s,t,e,r=.3,n){for(let o of t){let i=o.a??1,a=Math.min(1,Math.max(0,o.white));s.fillStyle=on(a,i,e,n),s.beginPath(),s.arc(o.x,o.y,o.r,0,Math.PI*2),s.fill()}}function ln(s,t,e,r){for(let n of t){let o=n.a??1,i=Math.min(1,Math.max(0,n.white));s.strokeStyle=on(i,o,e,r),s.lineWidth=n.w,s.beginPath(),s.moveTo(n.x1,n.y1),s.lineTo(n.x2,n.y2),s.stroke()}}function X(s,t,e=.3){let r=[];for(let n of s)(n.a??1)<.02||(n.r=Math.max(e,n.r),r.push(n));return r.sort((n,o)=>n.z-o.z),{dots:r,lines:t.filter(n=>(n.a??1)>=.02)}}function Se(s,t,e,r){t.lines.length&&ln(s,t.lines,e,r),an(s,t.dots,e,.3,r)}function ht(s,t){return(s/300)**t}var xo=[["latRings","lonDensity"],["rings","lonDensity"],["lanes","segs"]],wo=["orbitN","ghostN","nodeN","strandN","signals"],$o=["iconD"],Mo=["rBase","rDepth","rActive","rDot","ghostR","partR","partRDepth","nodeR","nodeRDepth"];function ko(s,t){let e={...s},r=new Set,n=Math.sqrt(t);for(let[o,i]of xo){let a=e[o],l=e[i];a!=null&&l!=null&&!r.has(o)&&!r.has(i)&&(e[o]=Math.max(2,Math.round(a*n)),e[i]=Math.max(2,Math.round(l*n)),r.add(o),r.add(i))}for(let o of wo){let i=e[o];i!=null&&i!==0&&!r.has(o)&&(e[o]=Math.max(1,Math.round(i*t)))}for(let o of $o){let i=e[o];i!=null&&(e[o]=Math.max(.02,i*t))}return e}function So(s,t){let e={...s};for(let r of Mo){let n=e[r];n!=null&&(e[r]=n*t)}return e.rSizeMul=(e.rSizeMul??1)*t,e}var Ao={globe:{latRings:17,lonDensity:44,rBase:.6,rDepth:1.7,rBoost:1,inkFar:.62,inkSpan:.54,rsPow:.6,rMin:.3},orbits:{orbitN:12,ghostN:40,ghostR:.9,ghostA:.5,particles:3,partR:1.2,partRDepth:1.6,rsPow:.6,rMin:.3},rubik:{latRings:15,lonDensity:40,moveCount:14,rBase:.6,rDepth:1.7,rActive:.3,inkFar:.62,inkSpan:.54,rsPow:.6,rMin:.3},wave:{rings:15,lonDensity:40,rBase:.6,rDepth:1.7,rsPow:.6,rMin:.3},web:{nodeN:30,thr:.72,signals:5,nodeR:1.4,nodeRDepth:1.8,lineW:.8,rsPow:.6,rMin:.3},braid:{strandN:52,turns:3,ghostN:150,rBase:1.2,rDepth:1.8,rsPow:.6,rMin:.3},ribbon:{lanes:5,segs:88,ghostN:150,rBase:1.1,rDepth:1.7,rsPow:.6,rMin:.3},ring:{lanes:5,segs:88,ghostN:0,faceOn:1,rBase:1.1,rDepth:1.7,rsPow:.6,rMin:.3},morph:{rDot:.021,iconD:1,rMin:.25}},Eo=(s,t,e)=>{let r=s/2,n=s/2,o=s/2*.76,i=ct(t*.4,.3,r,n,1),a=ht(s,e.rsPow??.6),l=[],c=e.ghostN??150;for(let u=0;u<c;u++){let p=ks(u,c),[m,g,f]=i(p[0]*o,p[1]*o,p[2]*o),b=(f/o+1)/2;l.push({x:m,y:g,z:f,r:.8*a,white:.78,a:.1+.22*b})}let d=e.strandN??52,h=e.turns??3;for(let u=0;u<3;u++){let p=u/3*2*Math.PI;for(let m=0;m<d;m++){let g=(nn(m/d+t*.045)*2-1)*.96,f=Math.sqrt(Math.max(0,1-g*g)),b=Math.min(1,(1-Math.abs(g))/.1),v=g*Math.PI*h+p,y=1+.075*Math.sin(g*Math.PI*h*2+p*2+t*.8),M=f*o*y,[_,S,k]=i(Math.cos(v)*M,g*o*y,Math.sin(v)*M),E=(k/o+1)/2;l.push({x:_,y:S,z:k,r:((e.rBase??1.2)+(e.rDepth??1.8)*E)*a,white:.55-.45*E,a:b*(.45+.55*E)})}}return X(l,[],e.rMin)};function Co(s,t,e,r){let n=2*t*e+r,o=s%n,i=new Array(t).fill(0),a=-1;if(o<2*t*e){let l=Math.floor(o/e),c=(o-l*e)/e,h=1-(1-Math.min(1,c/.7))**3;if(l<t){for(let u=0;u<l;u++)i[u]=1;i[l]=h,a=l}else{let u=2*t-1-l;for(let p=0;p<u;p++)i[p]=1;i[u]=1-h,a=u}}return{amount:i,active:a}}function Po(s,t,e){let[r,n,o]=s,i=!1;for(let a=0;a<t.length;a++){if(e.amount[a]<=0)continue;let l=t[a],c=l.axis===0?r:l.axis===1?n:o;if(c<l.lo||c>=l.hi)continue;a===e.active&&(i=!0);let d=l.ang*e.amount[a],h=Math.cos(d),u=Math.sin(d);if(l.axis===0){let p=n*h-o*u;o=n*u+o*h,n=p}else if(l.axis===1){let p=r*h+o*u;o=-r*u+o*h,r=p}else{let p=r*h-n*u;n=r*u+n*h,r=p}}return[r,n,o,i]}function zo(s){let t=[];for(let e=0;e<s;e++){let r=Math.min(2,Math.floor(B(e,2.3)*3)),n=-1+.5*Math.min(3,Math.floor(B(e,5.9)*4)),o=B(e,7.7)<.5?1:-1;t.push({axis:r,lo:n,hi:n+.5,ang:o*Math.PI/2})}return t}var Ro=(s,t,e)=>{let n=s/2,o=s/2,i=s/2*.82,a=.4+.06*Math.sin(t*.35),l=ct(t*.5,a,n,o,i),c=t*(.5+(1.7-.5)*(e.scanMul??1)),d=ht(s,e.rsPow??.6),h=e.dimBase??1,u=[],p=e.latRings??17,m=e.lonDensity??44;for(let g=0;g<=p;g++){let f=-Math.PI/2+g/p*Math.PI,b=Math.cos(f),v=Math.sin(f),y=Math.max(1,Math.round(Math.abs(b)*m));for(let M=0;M<y;M++){let _=M/y*2*Math.PI,[S,k,E]=l(b*Math.cos(_),v,b*Math.sin(_)),P=(E+1)/2,z=_o(_+t*.5,c),O=Math.exp(-(z*z)/.18)*Math.max(0,E);u.push({x:S,y:k,z:E,r:((e.rBase??.6)+(e.rDepth??1.7)*P+(e.rBoost??1)*O)*d,white:(e.inkFar??.62)-(e.inkSpan??.54)*P,a:h+(1-h)*Math.min(1,O)})}}return X(u,[],e.rMin)},Oo=(s,t,e)=>{let r=s/2,n=s/2,o=s/2*.82,i=ct(t*.55,.35+.1*Math.sin(t*.9),r,n,o),a=ht(s,e.rsPow??.6),l=e.moveCount??14,c=zo(l),d=Co(t,l,.42,1.2),h=[],u=e.latRings??15,p=e.lonDensity??40;for(let m=0;m<=u;m++){let g=-Math.PI/2+m/u*Math.PI,f=Math.cos(g),b=Math.sin(g),v=Math.max(1,Math.round(Math.abs(f)*p));for(let y=0;y<v;y++){let M=y/v*2*Math.PI,[_,S,k,E]=Po([f*Math.cos(M),b,f*Math.sin(M)],c,d),[P,z,O]=i(_,S,k),R=(O+1)/2;h.push({x:P,y:z,z:O,r:((e.rBase??.6)+(e.rDepth??1.7)*R+(E?e.rActive??.3:0))*a,white:(e.inkFar??.62)-(e.inkSpan??.54)*R-(E?.14:0)})}}return X(h,[],e.rMin)},To=(s,t,e)=>{let r=s/2,n=s/2,o=s/2*.874,i=ct(t*.18,.38,r,n,1),a=ht(s,e.rsPow??.6),l=[],c=e.rings??15,d=e.lonDensity??40;for(let h=0;h<=c;h++){let u=-Math.PI/2+h/c*Math.PI,p=Math.cos(u),m=Math.sin(u),g=.62*Math.sin(t*2.1-h*.52)+.38*Math.sin(t*1.27+h*.83),f=o*(.88+.105*g),b=Math.max(1,Math.round(Math.abs(p)*d));for(let v=0;v<b;v++){let y=v/b*2*Math.PI,[M,_,S]=i(p*Math.cos(y)*f,m*f,p*Math.sin(y)*f),k=(S/o+1)/2,E=Math.max(0,g);l.push({x:M,y:_,z:S,r:((e.rBase??.6)+(e.rDepth??1.7)*k)*(1+.4*E)*a,white:.66-.56*k-.1*E})}}return X(l,[],e.rMin)};function No(s){return s*s*(3-2*s)}function cn(s){let t=s.length,e=[],r=0;for(let n=0;n<t;n++){let o=s[n],i=s[(n+1)%t],a=Math.hypot(i[0]-o[0],i[1]-o[1]);e.push(a),r+=a}return n=>{let o=n*r,i=0;for(;o>e[i]&&i<t-1;)o-=e[i],i++;let a=s[i],l=s[(i+1)%t],c=e[i]?Math.min(1,o/e[i]):0;return[a[0]+(l[0]-a[0])*c,a[1]+(l[1]-a[1])*c]}}var Lo=s=>{let t=-Math.PI/2+s*2*Math.PI;return[Math.cos(t)*.24,Math.sin(t)*.24]},Do=cn([[0,-.26],[.24,.16],[-.24,.16]]),Io=cn([[0,-.2],[.2,-.2],[.2,.2],[-.2,.2],[-.2,-.2]]),$s=[Lo,Do,Io];function Uo(s){return Math.max(6,Math.round(34*s))}var Ms=1.4,hn=.9,ke=Ms+hn,qo=(s,t,e)=>{let r=$s.length,n=t%(ke*r),o=e.shape!=null&&e.shape>=0&&e.shape<r?Math.floor(e.shape):-1,i=o>=0?o:Math.floor(n/ke),a=o>=0?t%ke:n-i*ke,l=o>=0?0:a>Ms?No((a-Ms)/hn):0,c=e.spread??1,d=$s[i],h=o>=0?d:$s[(i+1)%r],u=160,p=[];for(let k=0;k<u;k++){let E=k/u,P=d(E),z=h(E);p.push([(P[0]+(z[0]-P[0])*l)*c,(P[1]+(z[1]-P[1])*l)*c])}let m=[],g=0;for(let k=0;k<u;k++){let E=p[k],P=p[(k+1)%u],z=Math.hypot(P[0]-E[0],P[1]-E[1]);m.push(z),g+=z}let f=Uo(e.iconD??1),b=(e.rDot??.021)*1.35*c,v=1+.02*Math.sin(a*3.1),y=[],M=s/2,_=0,S=0;for(let k=0;k<f;k++){let E=k/f*g;for(;S+m[_]<E&&_<u-1;)S+=m[_],_++;let P=p[_],z=p[(_+1)%u],O=m[_]?Math.min(1,(E-S)/m[_]):0,R=(P[0]+(z[0]-P[0])*O)*v,V=(P[1]+(z[1]-P[1])*O)*v;y.push({x:M+R*s,y:M+V*s,z:0,r:Math.max(.35,b*s),white:.1})}return X(y,[],e.rMin)},Ho=(s,t,e)=>{let r=s/2,n=s/2,o=s/2*.82,i=ct(t*.12,.3,r,n,1),a=ht(s,e.rsPow??.6),l=[],c=e.orbitN??12,d=e.ghostN??40,h=e.particles??3;for(let u=0;u<c;u++){let p=B(u,1.7),m=B(u,5.2),g=B(u,8.9),f=o*(.45+.52*p),b=p*2*Math.PI,v=Math.acos(2*m-1),y=Math.sin(v)*Math.cos(b),M=Math.cos(v),_=Math.sin(v)*Math.sin(b),S=-M,k=y,E=0,P=Math.max(1e-6,Math.sqrt(S*S+k*k));S/=P,k/=P;let z=M*E-_*k,O=_*S-y*E,R=y*k-M*S,V=(.25+.55*g)*(g>.5?1:-1);for(let H=0;H<d;H++){let N=H/d*2*Math.PI,[U,J,ut]=i((S*Math.cos(N)+z*Math.sin(N))*f,(k*Math.cos(N)+O*Math.sin(N))*f,(E*Math.cos(N)+R*Math.sin(N))*f),Q=(ut/f+1)/2;l.push({x:U,y:J,z:ut,r:(e.ghostR??.9)*a,white:.72,a:(e.ghostA??.5)*(.4+.6*Q)})}for(let H=0;H<h;H++){let N=t*V+H/h*2*Math.PI+m*6,[U,J,ut]=i((S*Math.cos(N)+z*Math.sin(N))*f,(k*Math.cos(N)+O*Math.sin(N))*f,(E*Math.cos(N)+R*Math.sin(N))*f),Q=(ut/f+1)/2;l.push({x:U,y:J,z:ut,r:((e.partR??1.2)+(e.partRDepth??1.6)*Q)*a,white:.3-.22*Q})}}return X(l,[],e.rMin)},sn=(s,t,e)=>{let r=s/2,n=s/2,o=s/2*.78,i=e.spin??1,a=.3,l=ct(t*.1*i,a,r,n,1),c=ht(s,e.rsPow??.6),d=[],h=e.ghostN??150;for(let R=0;R<h;R++){let V=ks(R,h),[H,N,U]=l(V[0]*o,V[1]*o,V[2]*o),J=(U/o+1)/2;d.push({x:H,y:N,z:U,r:.8*c,white:.78,a:.1+.22*J})}let u=t*.24*i,p=e.faceOn?-a:.55+.3*Math.sin(t*.18)*i,m=Math.cos(u),g=0,f=Math.sin(u),b=-f*Math.sin(p),v=Math.cos(p),y=m*Math.sin(p),M=g*y-f*v,_=f*b-m*y,S=m*v-g*b,k=.23*(e.wobMul??1),E=e.faceOn?o/(1+.85*k):o,P=e.lanes??5,z=e.segs??88,O=Math.max(1,Math.round(P*(e.bandMul??1)));for(let R=0;R<O;R++){let V=(R-(O-1)/2)*.075,H=Math.abs(R-(O-1)/2)/Math.max(1,(O-1)/2);for(let N=0;N<z;N++){let U=N/z*2*Math.PI,J=(.16*Math.sin(U*3-t*1.7+R*.22)+.07*Math.sin(U*5+t*1.1))*(e.wobMul??1),ut=e.faceOn?1+J:1,Q=e.faceOn?V:V+J,Ce=m*Math.cos(U)+b*Math.sin(U)+M*Q,Pe=g*Math.cos(U)+v*Math.sin(U)+_*Q,ze=f*Math.cos(U)+y*Math.sin(U)+S*Q,Re=Math.sqrt(Ce*Ce+Pe*Pe+ze*ze),Oe=E*ut,[bn,vn,zs]=l(Ce/Re*Oe,Pe/Re*Oe,ze/Re*Oe),Te=(zs/o+1)/2;d.push({x:bn,y:vn,z:zs,r:((e.rBase??1.1)+(e.rDepth??1.7)*Te)*(1-.25*H)*c,white:.52-.44*Te+.18*H,a:.4+.6*Te})}}return X(d,[],e.rMin)},jo=(s,t,e)=>{let r=s/2,n=s/2,o=s/2*.8*(e.spread??1),i=ct(t*.12,.32,r,n,o),a=ht(s,e.rsPow??.6),l=e.nodeN??30,c=e.thr??.72,d=e.nodeR??1.4,h=e.nodeRDepth??1.8,u=[];for(let f=0;f<l;f++){let b=ks(f,l),v=b[0]+.3*(ws(f*.31+9,t*.24)-.5)*2,y=b[1]+.3*(ws(f*.53+27,t*.21)-.5)*2,M=b[2]+.3*(ws(f*.77+55,t*.27)-.5)*2,_=Math.sqrt(v*v+y*y+M*M);u.push([v/_,y/_,M/_])}let p=[],m=[];for(let f=0;f<l;f++)for(let b=f+1;b<l;b++){let v=u[f][0]-u[b][0],y=u[f][1]-u[b][1],M=u[f][2]-u[b][2],_=Math.sqrt(v*v+y*y+M*M);if(_>=c)continue;let[S,k,E]=i(u[f][0],u[f][1],u[f][2]),[P,z,O]=i(u[b][0],u[b][1],u[b][2]),R=((E+O)/2+1)/2;p.push({x1:S,y1:k,x2:P,y2:z,white:.42,a:(1-_/c)*(.3+.55*R),w:Math.max(.6,(e.lineW??.8)*a)})}for(let f=0;f<l;f++){let[b,v,y]=i(u[f][0],u[f][1],u[f][2]),M=(y+1)/2,_=1+.25*Math.sin(t*1.4+f*2.7);m.push({x:b,y:v,z:y,r:(d+h*M)*_*a,white:.55-.45*M})}let g=e.signals??5;for(let f=0;f<g;f++){let b=Math.floor(t*.55+f*7.31),v=Math.floor(B(b,f*3.1+1.7)*l),y=Math.floor(B(b,f*5.7+4.2)*l);if(v===y)continue;let M=nn(t*.55+f*7.31),_=xs(u[v][0],u[y][0],M),S=xs(u[v][1],u[y][1],M),k=xs(u[v][2],u[y][2],M),E=Math.max(1e-6,Math.sqrt(_*_+S*S+k*k)),[P,z,O]=i(_/E,S/E,k/E),R=(O+1)/2;m.push({x:P,y:z,z:O,r:(d*1.5+h*R)*a,white:.05,a:.5+.5*R})}return X(m,p,e.rMin)},Ae={orbits:Ho,globe:Ro,rubik:Oo,wave:To,web:jo,braid:Eo,ribbon:sn,ring:sn,morph:qo},Bo=Object.fromEntries(Object.entries(Ae).map(([s,t])=>[s,(e,r,n,o,i)=>Se(e,t(r,n,i),o)])),dn={working:"orbits",searching:"globe",solving:"rubik",listening:"wave",connecting:"web",weaving:"braid",composing:"ribbon",breathing:"ring",shaping:"morph"},Fo={orbits:{64:{speed:1.885,count:1,size:1},32:{speed:2.9072,count:.4251,size:1.6849},20:{speed:3.9,count:.238,size:2.4}},globe:{64:{speed:2.015,count:.42,size:1.15,extra:{scanMul:4.08,dimBase:.45}},32:{speed:2.3803,count:.1839,size:1.4769,extra:{scanMul:4.2301,dimBase:.45}},20:{speed:2.665,count:.105,size:1.75,extra:{scanMul:4.335,dimBase:.45}}},rubik:{64:{speed:1.82,count:.35,size:1.05},32:{speed:1.8964,count:.1537,size:1.4951},20:{speed:1.95,count:.088,size:1.9}},wave:{64:{speed:4.388,count:.341,size:1},32:{speed:4.1512,count:.169,size:1.3232},20:{speed:3.998,count:.105,size:1.6}},web:{64:{speed:3.315,count:1.35,size:.95},32:{speed:5.0104,count:.4942,size:1.2571},20:{speed:6.63,count:.25,size:1.52}},braid:{64:{speed:1.625,count:.5,size:1},32:{speed:2.2234,count:.2056,size:1.2011},20:{speed:2.75,count:.1125,size:1.36}},ribbon:{64:{speed:2.34,count:.25,size:.85,extra:{spin:0,bandMul:3.9,wobMul:1}},32:{speed:2.7776,count:.0969,size:.9766,extra:{spin:0,bandMul:4.49,wobMul:1}},20:{speed:3.12,count:.051,size:1.073,extra:{spin:0,bandMul:4.94,wobMul:1}}},ring:{64:{speed:3.24,count:.25,size:.956,extra:{spin:0,bandMul:3.627,wobMul:.368}},32:{speed:3.5517,count:.0678,size:1.31,extra:{spin:0,bandMul:3.8265,wobMul:.4751}},20:{speed:3.78,count:.028,size:1.622,extra:{spin:0,bandMul:3.968,wobMul:.565}}},morph:{64:{speed:2.405,count:.702,size:.395,extra:{spread:1.45}},32:{speed:2.2057,count:.5937,size:.6916,extra:{spread:1.45}},20:{speed:2.08,count:.53,size:1.011,extra:{spread:1.45}}}},rn=new Map;function Ss(s,t){let e=`${s}-${t}`,r=rn.get(e);if(r)return r;let n=dn[s],o=Fo[n][t],i={...Ao[n]};o.count!==1&&(i=ko(i,o.count)),o.size!==1&&(i=So(i,o.size)),o.extra&&(i={...i,...o.extra});let a={mode:n,speed:o.speed,opts:i};return rn.set(e,a),a}function pn(s,t){return{handler:s,config:t}}pn.withOptions=function(s,t=()=>({})){function e(r){return{handler:s(r),config:t(r)}}return e.__isOptionsFunction=!0,e};var Vo=pn,Wo=`
class SquirclePainter {
  static get inputProperties() {
    return [
      '--tw-squircle-w',
      '--tw-squircle-smooth',
      'border-top-left-radius',
      'border-radius'
    ];
  }
  
  paint(ctx, size, properties) {
    const getProp = (name) => {
      const p = properties.get(name);
      if (!p) return '';
      if (typeof p.value === 'number') return p.value + (p.unit || 'px');
      return p.toString().trim();
    };
    
    const radiusStr = getProp('--tw-squircle-w') || getProp('border-top-left-radius') || getProp('border-radius');
    let radius = 0;
    if (radiusStr) {
      const firstVal = radiusStr.trim().split(/s+/)[0];
      if (firstVal.endsWith('%')) {
        radius = (Math.min(size.width, size.height) * parseFloat(firstVal)) / 100;
      } else {
        const parsed = parseFloat(firstVal);
        if (firstVal.endsWith('rem')) {
          radius = parsed * 16;
        } else {
          radius = parsed || 0;
        }
      }
    }
    const smoothStr = getProp('--tw-squircle-smooth');
    let smooth = parseFloat(smoothStr);
    if (isNaN(smooth)) smooth = 0.6;
    
    radius = Math.min(radius, size.width / 2, size.height / 2);
    
    this.drawSquircle(ctx, size.width, size.height, radius, smooth);
    ctx.fillStyle = 'black';
    ctx.fill();
  }
  
  drawSquircle(ctx, width, height, radius, smooth) {
    const n = 2 + smooth * 2;
    const steps = 30;
    const step = Math.PI / 2 / steps;
    ctx.beginPath();
    for (let i = 0; i <= steps; i++) {
      const t = Math.PI / 2 - i * step;
      const X = radius * Math.pow(Math.cos(t), 2 / n);
      const Y = radius * Math.pow(Math.sin(t), 2 / n);
      const x = width - radius + X;
      const y = radius - Y;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    for (let i = 0; i <= steps; i++) {
      const t = i * step;
      const X = radius * Math.pow(Math.cos(t), 2 / n);
      const Y = radius * Math.pow(Math.sin(t), 2 / n);
      ctx.lineTo(width - radius + X, height - radius + Y);
    }
    for (let i = 0; i <= steps; i++) {
      const t = Math.PI / 2 - i * step;
      const X = radius * Math.pow(Math.cos(t), 2 / n);
      const Y = radius * Math.pow(Math.sin(t), 2 / n);
      ctx.lineTo(radius - X, height - radius + Y);
    }
    for (let i = 0; i <= steps; i++) {
      const t = i * step;
      const X = radius * Math.pow(Math.cos(t), 2 / n);
      const Y = radius * Math.pow(Math.sin(t), 2 / n);
      ctx.lineTo(radius - X, radius - Y);
    }
    ctx.closePath();
  }
}

class SquircleBorderPainter extends SquirclePainter {
  static get inputProperties() {
    return [
      '--tw-squircle-w', 
      '--tw-squircle-smooth',
      'border-top-left-radius',
      'border-radius',
      'border-top-width',
      'border-top-color'
    ];
  }
  
  paint(ctx, size, properties) {
    const getProp = (name) => {
      const p = properties.get(name);
      if (!p) return '';
      if (typeof p.value === 'number') return p.value + (p.unit || 'px');
      return p.toString().trim();
    };

    const radiusStr = getProp('--tw-squircle-w') || getProp('border-top-left-radius') || getProp('border-radius');
    let radius = 0;
    if (radiusStr) {
      const firstVal = radiusStr.trim().split(/s+/)[0];
      if (firstVal.endsWith('%')) {
        radius = (Math.min(size.width, size.height) * parseFloat(firstVal)) / 100;
      } else {
        const parsed = parseFloat(firstVal);
        if (firstVal.endsWith('rem')) {
          radius = parsed * 16;
        } else {
          radius = parsed || 0;
        }
      }
    }
    const smoothStr = getProp('--tw-squircle-smooth');
    let smooth = parseFloat(smoothStr);
    if (isNaN(smooth)) smooth = 0.6;
    
    radius = Math.min(radius, size.width / 2, size.height / 2);
    
    const bwStr = getProp('border-top-width');
    const bw = parseFloat(bwStr) || 0;
    
    if (bw <= 0) return;
    
    let color = getProp('border-top-color');
    if (!color) color = 'black';
    
    // Inset stroke by half border-width so it stays 100% within the element bounds
    const halfBw = bw / 2;
    const innerW = Math.max(0, size.width - bw);
    const innerH = Math.max(0, size.height - bw);
    const innerR = Math.max(0, radius - halfBw);
    
    ctx.save();
    ctx.translate(halfBw, halfBw);
    this.drawSquircle(ctx, innerW, innerH, innerR, smooth);
    ctx.lineWidth = bw;
    ctx.strokeStyle = color;
    ctx.stroke();
    ctx.restore();
  }
}

registerPaint('squircle', SquirclePainter);
registerPaint('squircle-border', SquircleBorderPainter);
`,un=!1;function fn(){if(typeof window<"u"&&"CSS"in window){if(un)return;if(un=!0,typeof CSS.supports=="function"&&CSS.supports("corner-shape","squircle")){document&&document.documentElement&&document.documentElement.classList.add("squircle-native");return}if("registerProperty"in CSS)try{CSS.registerProperty({name:"--tw-squircle-w",syntax:"<length> | <percentage>",inherits:!0,initialValue:"0px"}),CSS.registerProperty({name:"--tw-squircle-smooth",syntax:"<number>",inherits:!0,initialValue:"0.6"})}catch{}if("paintWorklet"in CSS){let s=`data:application/javascript;charset=utf8,${encodeURIComponent(Wo)}`;CSS.paintWorklet.addModule(s).then(()=>{document&&document.documentElement&&document.documentElement.classList.add("squircle-ready")}).catch(t=>console.error("Squircle worklet failed",t))}}}var Ih=Vo(function({addUtilities:s,matchUtilities:t,theme:e}){t({squircle:(r,{modifier:n})=>{let o=.6;if(n){let i=parseFloat(n);isNaN(i)||(o=i>1?i/100:i)}return{"--tw-squircle-smooth":o.toString(),"@supports (corner-shape: squircle)":{"corner-shape":"squircle"},"@supports (not (corner-shape: squircle)) and (mask-image: paint(squircle))":{":where(html.squircle-ready) &":{"mask-image":"paint(squircle)","-webkit-mask-image":"paint(squircle)",'&[class~="border"], &[class*=" border-"], &[class^="border-"]':{"border-image-source":"paint(squircle-border)","border-image-slice":"0 fill","border-image-outset":"var(--tw-squircle-outset, 0)"},"a&, input&, a &, input &":{"mask-image":"none","-webkit-mask-image":"none","background-image":"paint(squircle)","border-image-source":"none"}}}}}},{values:{DEFAULT:"DEFAULT"},modifiers:{0:"0",20:"20",40:"40",60:"60",80:"80",100:"100"}}),t({squircle:(r,{modifier:n})=>{let o=.6;if(n){let i=parseFloat(n);isNaN(i)||(o=i/100)}return{"border-radius":r,"--tw-squircle-w":r,"--tw-squircle-smooth":o.toString(),"@supports (corner-shape: squircle)":{"corner-shape":"squircle"},"@supports (not (corner-shape: squircle)) and (mask-image: paint(squircle))":{":where(html.squircle-ready) &":{"border-radius":"0","mask-image":"paint(squircle)","-webkit-mask-image":"paint(squircle)",'&[class~="border"], &[class*=" border-"], &[class^="border-"]':{"border-image-source":"paint(squircle-border)","border-image-slice":"0 fill","border-image-outset":"var(--tw-squircle-outset, 0)"},"a&, input&, a &, input &":{"border-radius":r,"mask-image":"none","-webkit-mask-image":"none","background-image":"paint(squircle)","border-image-source":"none"}}}}}},{values:e("borderRadius"),modifiers:{0:"0",20:"20",40:"40",60:"60",80:"80",100:"100"}})});try{fn()}catch{}var ce=matchMedia("(prefers-reduced-motion: reduce)");function mn(){let s=document.documentElement.getAttribute("data-theme");return s==="dark"?!0:s==="light"?!1:matchMedia("(prefers-color-scheme: dark)").matches}var As=class extends HTMLElement{connectedCallback(){let t=Number(this.getAttribute("size")||64),e=this.getAttribute("state")||"listening",r=document.createElement("canvas");r.setAttribute("role","img"),r.setAttribute("aria-label",this.getAttribute("label")||"Clari is listening"),r.style.cssText=`width:${t}px;height:${t}px;display:block;max-width:100%;height:auto;aspect-ratio:1`,this.replaceChildren(r);let n=Math.min(2,devicePixelRatio||1);r.width=Math.round(t*n),r.height=Math.round(t*n);let o=r.getContext("2d"),{mode:i,speed:a,opts:l}=Ss(e,64),c=Ae[i],d=Number(this.getAttribute("speed")||1),h=()=>{let S=getComputedStyle(this).color.match(/(\d+)\D+(\d+)\D+(\d+)/);return S?{r:+S[1],g:+S[2],b:+S[3]}:void 0},u=h(),p=mn(),m=n*t/64,g=S=>{o.setTransform(m,0,0,m,0,0),o.clearRect(0,0,64,64),Se(o,c(64,S,l),p,u)},f=0,b=!1,v=!0,y=()=>{g(performance.now()/1e3*a*d),b&&(f=requestAnimationFrame(y))},M=()=>{b||ce.matches||(b=!0,f=requestAnimationFrame(y))},_=()=>{b=!1,cancelAnimationFrame(f)};g(.6),this._io=new IntersectionObserver(([S])=>{v=S.isIntersecting,v&&!document.hidden?M():_()}),this._io.observe(r),this._vis=()=>document.hidden?_():v&&M(),document.addEventListener("visibilitychange",this._vis),this._theme=()=>{p=mn(),u=h(),b||g(.6)},matchMedia("(prefers-color-scheme: dark)").addEventListener("change",this._theme),this._mo=new MutationObserver(this._theme),this._mo.observe(document.documentElement,{attributes:!0,attributeFilter:["data-theme"]}),this._motion=()=>{ce.matches?(_(),g(.6)):v&&M()},ce.addEventListener("change",this._motion)}disconnectedCallback(){this._io?.disconnect(),this._mo?.disconnect(),document.removeEventListener("visibilitychange",this._vis),ce.removeEventListener("change",this._motion)}};customElements.define("clari-orb",As);function Ee(s){let t=s>>>0;return()=>(t=t*1664525+1013904223>>>0,t/4294967296)}var Es=(s,t)=>(s()-.5)*2*t,dt=s=>Math.round(s*100)/100;function qt(s,t=!1){let[e,...r]=s,n=`M${dt(e.x)},${dt(e.y)}`;return r.forEach((o,i)=>{let a=r[i+1];n+=a?` Q${dt(o.x)},${dt(o.y)} ${dt((o.x+a.x)/2)},${dt((o.y+a.y)/2)}`:` L${dt(o.x)},${dt(o.y)}`}),t?n+" Z":n}function zt(s,t,{sag:e=0,wobble:r=.55,steps:n=12},o){let i=[];for(let a=0;a<=n;a++){let l=a/n,c=a===0||a===n?0:1;i.push({x:s.x+(t.x-s.x)*l+Es(o,r)*c,y:s.y+(t.y-s.y)*l+Math.sin(l*Math.PI)*e+Es(o,r)*c})}return i}function gn(s,{rx:t,ry:e},{from:r,to:n},{wobble:o=.03,steps:i=28},a){let l=[];for(let c=0;c<=i;c++){let d=(r+(n-r)*(c/i))*Math.PI/180,h=1+Es(a,o);l.push({x:s.x+Math.cos(d)*t*h,y:s.y+Math.sin(d)*e*h})}return l}var Go={underline:{viewBox:"0 0 140 10",cls:"mk-underline",strokes:(()=>{let s=Ee(23);return[{d:qt(zt({x:3,y:6},{x:137,y:5},{sag:-2},s))}]})()},doubleUnderline:{viewBox:"0 0 140 16",cls:"mk-double",strokes:(()=>{let s=Ee(41);return[{d:qt(zt({x:3,y:5},{x:137,y:4},{sag:-2},s))},{d:qt(zt({x:5,y:12},{x:135,y:11},{sag:-1.2},s)),width:1.8,opacity:.75}]})()},circle:{viewBox:"0 0 220 64",cls:"mk-circle",strokes:(()=>{let s=Ee(101);return[{d:qt(gn({x:110,y:32},{rx:100,ry:27},{from:150,to:520},{wobble:.035},s)),width:3},{d:qt(gn({x:110,y:32},{rx:95,ry:24},{from:165,to:480},{wobble:.03},s)),width:1.5,opacity:.55}]})()},highlight:{viewBox:"0 0 170 26",cls:"mk-highlight",behind:!0,strokes:(()=>{let s=Ee(163);return[{fill:!0,d:qt([...zt({x:5,y:6},{x:165,y:5},{sag:-2,steps:10},s),...zt({x:165,y:5},{x:165,y:21},{steps:3},s),...zt({x:165,y:21},{x:5,y:22},{sag:2,steps:10},s),...zt({x:5,y:22},{x:5,y:6},{steps:3},s)],!0)}]})()}},Cs=class extends HTMLElement{connectedCallback(){if(this._done)return;this._done=!0;let t=Go[this.getAttribute("variant")||"underline"],e="http://www.w3.org/2000/svg",r=document.createElementNS(e,"svg");r.setAttribute("viewBox",t.viewBox),r.setAttribute("fill","none"),r.setAttribute("preserveAspectRatio","none"),r.setAttribute("aria-hidden","true"),r.setAttribute("class","mk "+t.cls);let n=t.strokes.map(l=>{let c=document.createElementNS(e,"path");return c.setAttribute("d",l.d),c.setAttribute("pathLength","1"),l.fill?c.setAttribute("fill","currentColor"):(c.setAttribute("stroke","currentColor"),c.setAttribute("stroke-width",String(l.width??2.4)),c.setAttribute("stroke-linecap","round"),c.setAttribute("stroke-linejoin","round"),c.setAttribute("vector-effect","non-scaling-stroke")),l.opacity&&c.setAttribute("opacity",String(l.opacity)),c.dataset.reveal=l.fill?"reveal":"stroke",r.append(c),c});if(t.behind){let l=document.createElement("span");l.className="mk-text",l.append(...this.childNodes),this.append(l),this.prepend(r)}else this.append(r);if(ce.matches)return;let o=Number(this.getAttribute("delay")||0)*1e3,i=n.map((l,c)=>{let d=Number(l.getAttribute("opacity")??1),h=l.animate(l.dataset.reveal==="reveal"?[{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0% 0 0)"}]:[{strokeDasharray:"1",strokeDashoffset:"1",opacity:0,offset:0},{strokeDasharray:"1",strokeDashoffset:"0.999",opacity:d,offset:.001},{strokeDasharray:"1",strokeDashoffset:"0",opacity:d,offset:1}],{duration:750,delay:o+c*160,easing:"cubic-bezier(0.22, 0.61, 0.36, 1)",fill:"backwards"});return h.pause(),h}),a=new IntersectionObserver(([l])=>{l.isIntersecting&&(i.forEach(c=>c.play()),a.disconnect())},{threshold:.25});a.observe(this)}};customElements.define("clari-mark",Cs);var Ko={g:{cls:"cal-g",word:"Their usual self",icon:"check"},y:{cls:"cal-y",word:"Keep an eye on it",icon:"q"},r:{cls:"cal-r",word:"Call their doctor",icon:"bang"},m:{cls:"cal-m",word:"Missed check-in, family texted",icon:"q"}},Yo={check:'<path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>',q:'<path d="M9 9.2a3 3 0 1 1 4.2 2.8c-.8.4-1.2 1-1.2 1.9v.6" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><circle cx="12" cy="18.3" r="1.7" fill="currentColor"/>',bang:'<path d="M12 5v9" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/><circle cx="12" cy="18.6" r="1.9" fill="currentColor"/>'},Ps=class extends HTMLElement{connectedCallback(){if(this._done)return;this._done=!0;let t=(this.getAttribute("days")||"").replace(/\s/g,"").split(""),e=new Date(this.getAttribute("end")||"2026-10-21T12:00:00"),r=new Intl.DateTimeFormat("en-US",{weekday:"short",month:"short",day:"numeric"}),n=document.createElement("div");n.className="cal-grid",n.setAttribute("role","list");let o=document.createElement("div");o.className="cal-tip",o.hidden=!0,o.setAttribute("aria-hidden","true");let i=new Date(e);i.setDate(e.getDate()-(t.length-1));let a=(i.getDay()+6)%7;for(let c=0;c<a;c++){let d=document.createElement("span");d.className="cal-cell cal-pad",d.setAttribute("aria-hidden","true"),n.append(d)}t.forEach((c,d)=>{let h=Ko[c],u=new Date(i);u.setDate(i.getDate()+d);let p=document.createElement("span");p.className="cal-cell squircle "+(h?h.cls:"cal-none"),p.style.setProperty("--i",String(d)),p.setAttribute("role","listitem");let m=`${r.format(u)}: ${h?h.word:"no check-in"}`;p.setAttribute("aria-label",m),h&&c!=="g"&&(p.innerHTML=`<svg viewBox="0 0 24 24" aria-hidden="true">${Yo[h.icon]}</svg>`);let g=()=>{o.textContent=m,o.hidden=!1;let f=n.getBoundingClientRect(),b=p.getBoundingClientRect();o.style.left=`${b.left-f.left+b.width/2}px`,o.style.top=`${b.top-f.top}px`};p.tabIndex=0,p.addEventListener("mouseenter",g),p.addEventListener("focus",g),p.addEventListener("mouseleave",()=>o.hidden=!0),p.addEventListener("blur",()=>o.hidden=!0),n.append(p)});let l=document.createElement("div");l.className="cal-wrap",l.append(n,o),this.replaceChildren(l)}};customElements.define("clari-calendar",Ps);
