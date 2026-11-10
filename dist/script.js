// La demo publicada clasifica con reglas JavaScript; Flask llama al modelo de app.py.
const mode = document.body.dataset.mode;
const messages = document.querySelector('#messages');
const quick = document.querySelector('#quick');
const input = document.querySelector('#input');
const form = document.querySelector('#form');
let state = {};
let busy = false;
function bubble(text,who='bot',typing=false){const row=document.createElement('div');row.className=`message ${who}`;if(who==='bot'){const avatar=document.createElement('div');avatar.className='mini-avatar';avatar.textContent='✳';row.append(avatar)}const body=document.createElement('div');body.className='bubble'+(typing?' typing':'');if(typing)body.innerHTML='<i></i><i></i><i></i>';else body.textContent=text;row.append(body);messages.append(row);messages.scrollTop=messages.scrollHeight;return row}
function options(items){quick.replaceChildren();for(const label of items){const button=document.createElement('button');button.type='button';button.dataset.message=label;button.textContent=label;quick.append(button)}}
const defaults=MENU.map(label=>[label,label]);
function defaultOptions(){quick.replaceChildren();const items=state.dni?[['Saldo','Consultar saldo'],['Mi score','Mi score'],['Tarjetas','Mi TC'],['Alias y CBU','Mi alias'],['Préstamos','Cotizar un préstamo'],['Transferencias','Consultar transferencia']]:defaults;for(const [label,value] of items){const b=document.createElement('button');b.type='button';b.dataset.message=value;b.textContent=label;quick.append(b)}}
async function send(message){
 if(busy||!message.trim())return;
 busy=true;input.value='';bubble(message,'user');options([]);
 const indicator=bubble('', 'bot',true);
 let closed=false;
 try{
   let answer;
   if(mode==='flask'){
     const response=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mensaje:message})});
     if(!response.ok)throw Error('No se pudo responder');
     answer=await response.json();
   }else answer=localAnswer(message);
   await new Promise(resolve=>setTimeout(resolve,650));
   closed=!!answer.cerrar_sesion;
   if(closed){
     messages.replaceChildren();
     const day=document.createElement('div');day.className='day';day.textContent='HOY';messages.append(day);
     bubble(message,'user');bubble(answer.texto);
   }else{
     indicator.querySelector('.bubble').classList.remove('typing');
     indicator.querySelector('.bubble').textContent=answer.texto;
   }
   document.querySelector('#client').textContent=answer.cliente?'Cuenta de '+answer.cliente:'Visitante · Consultas sin cuenta';
   const panel=document.querySelector('#profile');panel.hidden=!answer.perfil;
   document.querySelector('#identity-card').hidden=!!answer.perfil;
   if(answer.perfil){
     document.querySelector('#profile-name').textContent=answer.cliente;
     document.querySelector('#profile-saldo').textContent=money(answer.perfil.saldo);
     document.querySelector('#profile-tc').textContent=money(answer.perfil.tc);
   }
   if(mode==='flask')state=answer.estado||{};if(answer.opciones?.length)options(answer.opciones);else defaultOptions();
 }catch{
   indicator.querySelector('.bubble').classList.remove('typing');
   indicator.querySelector('.bubble').textContent='Hubo un problema. Volvé a intentar.';
   defaultOptions();
 }finally{busy=false;messages.scrollTop=messages.scrollHeight;if(!closed)input.focus()}
}
form.addEventListener('submit',event=>{event.preventDefault();send(input.value)});quick.addEventListener('click',event=>{const button=event.target.closest('button[data-message]');if(button)send(button.dataset.message)});
document.querySelector('#reset').addEventListener('click',async()=>{if(busy)return;if(mode==='flask')await fetch('/api/reiniciar',{method:'POST'});state={};document.querySelector('#client').textContent='Visitante · Consultas sin cuenta';document.querySelector('#profile').hidden=true;document.querySelector('#identity-card').hidden=false;messages.replaceChildren();const day=document.createElement('div');day.className='day';day.textContent='HOY';messages.append(day);bubble('¡Hola! Soy Nova. Consultá productos o cotizá un préstamo, aunque no seas cliente. ¿En qué te ayudo?');defaultOptions();input.focus()});
const dialog=document.querySelector('#about');document.querySelector('#info').onclick=()=>dialog.showModal();document.querySelector('#close').onclick=()=>dialog.close();dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});

// Optional browser agent entry point. It uses the same chat action as the UI.
if (document.modelContext?.registerTool) {
  try { Promise.resolve(document.modelContext.registerTool({
    name:'send_nova_message', title:'Consultar a Nova',
    description:'Enviar un mensaje al chatbot ficticio y mostrarlo en la conversación.',
    inputSchema:{type:'object',properties:{message:{type:'string'}},required:['message'],additionalProperties:false},
    annotations:{readOnlyHint:false,untrustedContentHint:false},
    async execute(args){if(typeof args?.message!=='string'||!args.message.trim()||args.message.length>500)throw Error('Mensaje inválido');await send(args.message);return {shown:true}}
  })).catch(()=>{}); } catch {}
}

// El teclado de iPhone no siempre modifica 100dvh. visualViewport sí informa
// la altura realmente visible, así el campo de texto queda sobre el teclado.
function syncMobileViewport(){
  if(!window.matchMedia('(max-width:720px)').matches){
    document.documentElement.style.removeProperty('--chat-viewport-height');
    document.documentElement.style.removeProperty('--chat-viewport-top');
    document.body.classList.remove('keyboard-open');
    return;
  }
  const viewport=window.visualViewport;
  document.documentElement.style.setProperty('--chat-viewport-height',Math.round(viewport?.height||window.innerHeight)+'px');
  document.documentElement.style.setProperty('--chat-viewport-top',Math.round(viewport?.offsetTop||0)+'px');
  document.body.classList.toggle('keyboard-open',document.activeElement===input);
  messages.scrollTop=messages.scrollHeight;
}
window.visualViewport?.addEventListener('resize',syncMobileViewport);
window.visualViewport?.addEventListener('scroll',syncMobileViewport);
window.addEventListener('resize',syncMobileViewport);
input.addEventListener('focus',()=>requestAnimationFrame(syncMobileViewport));
input.addEventListener('blur',()=>setTimeout(syncMobileViewport,100));
syncMobileViewport();

defaultOptions();
