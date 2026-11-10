// Motor de la demo web: reglas JavaScript. La versión Flask clasifica con RL.
const INICIO = "¡Hola! Soy Nova. Puedo contarte sobre nuestras cuentas y tarjetas, cotizar un préstamo o ayudarte con tus productos. No necesitás ser cliente para consultar. ¿En qué te ayudo?";
const MENU = ["Ver productos", "Cotizar un préstamo", "Soy cliente", "Hablar con un asesor"];
const CLIENTES = {"12345678": {"nombre": "Camila", "saldo": 1044000, "tc": 327200, "limite": 2500000, "limite_tc": 1200000, "transferencia": 30600, "dia": 16}, "87654321": {"nombre": "Martín", "saldo": 612000, "tc": 198000, "limite": 1500000, "limite_tc": 900000, "transferencia": 45000, "dia": 18}, "23456789": {"nombre": "Lucía", "saldo": 386500, "tc": 84500, "limite": 1000000, "limite_tc": 650000, "transferencia": 22000, "dia": 20}, "34567890": {"nombre": "Tomás", "saldo": 1590000, "tc": 412000, "limite": 3000000, "limite_tc": 1800000, "transferencia": 68000, "dia": 22}, "45678901": {"nombre": "Sofía", "saldo": 725000, "tc": 156300, "limite": 2000000, "limite_tc": 1000000, "transferencia": 31500, "dia": 24}, "56789012": {"nombre": "Julián", "saldo": 215000, "tc": 68900, "limite": 1000000, "limite_tc": 500000, "transferencia": 18000, "dia": 25}};
const PUBLICAS = {"productos": "En BUAInco podés conocer la caja de ahorro, tarjetas de débito y crédito, y préstamos personales. También podés cotizar sin ser cliente. ¿Qué te interesa?", "asesor": "Podés comunicarte con un asesor desde el número 0800-000-2824 de BUAInco - opción 2"};
const TNA = .79, PLAZOS = [6,12,24], LIMITE_VISITANTE = 1000000;
const PERSONALES = ['saldo','tc','td','alias','transferencia','tarjeta_perdida','score'];
const normal = s => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
const has = (t,p) => new RegExp('(^|[^\\w])'+p.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'($|[^\\w])').test(t);
const money = n => '$'+n.toLocaleString('es-AR');
function baseState(s){return Object.fromEntries(['dni','bloqueadas'].filter(k=>k in s).map(k=>[k,s[k]]))}
function profile(s){return s.dni?(CLIENTES[s.dni]||profileForDni(s.dni)):null}
function result(texto,estado,opciones=[]){const p=profile(estado);return {texto,estado,opciones,cliente:p?.nombre||null,perfil:p?{saldo:p.saldo,tc:p.tc}:null}}
function profileForDni(dni){const n=Number(dni);return {nombre:'Cliente',saldo:180000+n%73*13500,tc:42000+n%59*6200,limite:1000000+n%5*500000,limite_tc:600000+n%5*200000,transferencia:12000+n%17*3100,dia:10+n%12}}
function scoreFor(s){const p=profile(s);return Math.round(650+2*Number(s.dni.slice(-2))-120*p.tc/p.limite_tc)}
function evaluation(s){const p=profile(s),score=scoreFor(s),risk=score>=740?'bajo':score>=650?'moderado':'alto';return `Evaluación crediticia · Central de Deudores\nScore BUAInco: ${score}/900 · Riesgo ${risk}\nLímite de préstamo personal del perfil: ${money(p.limite)}\nConsulta recreada con datos ficticios del perfil; no se accede a una central externa. El DNI de prueba se mantiene durante la sesión y se elimina al cerrarla. No se guarda en una base de datos.`}
function classify(message){
 const t=normal(message);
 if(['perdi','perdida','robaron','bloquear','extravie','no encuentro','se me perdio','me afanaron','extravio','anular'].some(x=>has(t,x)))return 'tarjeta_perdida';
 if(/limite|disponible para comprar|cupo|credito me queda/.test(t))return 'tc';
 if(/alias|\bcbu\b|datos para (recibir|transferir)|datos bancarios|manden plata/.test(t))return 'alias';
 if(/\bscore\b|scoring|calificacion crediticia|central de deudores|historial crediticio|mis deudas/.test(t))return 'score';
 if(/productos|que (ofrecen|tienen)|que tarjetas ofrecen|que cuentas ofrecen|conocer el banco|servicios|opciones bancarias|que es.*(cuenta|caja|tarjeta)|como funciona.*(cuenta|caja|tarjeta)/.test(t))return 'productos';
 for(const [sigla,intent] of [['pp','prestamo'],['tc','tc'],['td','td']])if(has(t,sigla))return intent;
 const terms={prestamo:['prestamo','credito personal','pedir plata','financiacion','plata prestada','cotizar','cuotas','meses'],saldo:['saldo','cuanto tengo','cuanto dinero tengo','cuanta plata','cuanta guita','dinero disponible','plata disponible','cuanto me queda','caja de ahorro','mi cuenta'],tc:['tarjeta de credito','tarjeta credito','resumen','vencimiento','vence','cierre','consumos','cuanto debo'],td:['tarjeta de debito','tarjeta debito','mi debito','extraer de cajero'],transferencia:['transferencia','transferi','envie dinero','envie plata','comprobante','giro','llego el dinero'],asesor:['asesor','persona','humano','atencion al cliente','representante','operador','soporte','hablar con alguien']};
 let best=null,max=0;for(const [intent,phrases] of Object.entries(terms)){const n=phrases.reduce((a,p)=>a+(has(t,p)?p.includes(' ')?3:1:0),0);if(n>max){best=intent;max=n}}return best;
}
function parseLoan(message,step){
 let t=normal(message),term=t.match(/\b(\d+)\s*(?:cuotas?|meses?)\b/),cuotas=term?Number(term[1]):null;
 if(term)t=t.slice(0,term.index)+t.slice(term.index+term[0].length);
 if(step==='cuotas'&&/^\s*\d+\s*$/.test(t))return [null,Number(t)];
 const m=t.match(/(?:^|[^\w])(\d{1,3}(?:\.\d{3})+|\d+(?:[.,]\d+)?)(?:\s*(millones?|millon|mil|k))?\b/);
 let monto=null;if(m){let v=m[1];if(/^\d{1,3}(?:\.\d{3})+$/.test(v))v=v.replaceAll('.','');monto=Math.round(Number(v.replace(',','.'))*(['millon','millones'].includes(m[2])?1000000:['mil','k'].includes(m[2])?1000:1));if(/-\s*\d/.test(message))monto=-Math.abs(monto)}return [monto,cuotas];
}
function payment(monto,cuotas,tna=TNA){const r=tna/12;return Math.round(monto*r/(1-(1+r)**(-cuotas)))}
function assessLoan(s,income){const p=profile(s),score=scoreFor(s),tna=score>=760?.69:score>=700?.79:score>=650?.95:1.15,monto=s.ultimo_prestamo,term=s.ultimas_cuotas,cuota=payment(monto,term,tna),effort=cuota/income,reasons=[];if(score<700)reasons.push('score inferior a 700');if(monto>p.limite)reasons.push('monto superior al límite del perfil');if(effort>.30)reasons.push('la cuota supera el 30% del ingreso declarado');const decision=reasons.length?'No preaprobado: '+reasons.join('; '):'Preaprobado según las reglas del ejercicio';return result(`Evaluación de préstamo personal\nMonto: ${money(monto)} · ${term} cuotas\nScore: ${score}/900 · TNA del perfil: ${Math.round(tna*100)}%\nCuota calculada: ${money(cuota)} · Total: ${money(cuota*term)}\nIngreso mensual declarado: ${money(income)} · Relación cuota/ingreso: ${(effort*100).toFixed(1)}%\nResultado: ${decision}.\nCriterios: score mínimo 700, cuota hasta el 30% del ingreso y monto dentro del límite. Resultado académico con datos de prueba; no genera una solicitud ni desembolso.`,baseState(s),['Cotizar otro monto','Mi score'])}
function quote(monto,cuotas,s){const cuota=payment(monto,cuotas);return result(`Préstamo personal de ${money(monto)}\n${cuotas} cuotas estimadas de ${money(cuota)}\nTotal estimado: ${money(cuota*cuotas)}\nTNA: 79% · Sistema francés\nCotización orientativa, sin impuestos ni otros cargos (CFT). No implica aprobación.`,{...baseState(s),ultimo_prestamo:monto,ultimas_cuotas:cuotas},['Evaluar mi préstamo','Mejor en 6 cuotas','Mejor en 12 cuotas','Mejor en 24 cuotas'])}
function advanceLoan(message,s){
 let [monto,cuotas]=parseLoan(message,s.paso);const limit=profile(s)?.limite||LIMITE_VISITANTE;
 monto=monto??s.monto;cuotas=cuotas??s.cuotas;const next=baseState(s);
 if(monto!=null&&(monto<100000||monto>limit))return result(`El monto debe estar entre $100.000 y ${money(limit)}. ¿Qué monto querés cotizar?`,{...next,paso:'monto'},['300 mil','500 mil','Cancelar']);
 if(monto!=null)next.monto=monto;
 if(cuotas!=null&&!PLAZOS.includes(cuotas))return result('Los plazos disponibles son 6, 12 o 24 cuotas. ¿Cuál elegís?',{...next,paso:monto?'cuotas':'monto'},['6 cuotas','12 cuotas','24 cuotas']);
 if(cuotas)next.cuotas=cuotas;
 if(!monto)return result(`Podés cotizar entre $100.000 y ${money(limit)}, en 6, 12 o 24 cuotas. ¿Qué monto necesitás?`,{...next,paso:'monto'},['300 mil en 12 cuotas','500 mil en 24 cuotas']);
 if(!cuotas)return result(`Para ${money(monto)}, ¿preferís 6, 12 o 24 cuotas?`,{...next,paso:'cuotas'},['6 cuotas','12 cuotas','24 cuotas']);
 return quote(monto,cuotas,s);
}
const formatDate=d=>[d.getDate(),d.getMonth()+1,d.getFullYear()].map((v,i)=>i<2?String(v).padStart(2,'0'):v).join('/');
function respond(message,s){
 const t=normal(message.trim()),social=t.replace(/[¿?¡!.,]+/g,'').trim(),p=profile(s),base=baseState(s),step=s.paso;
 if(['chau','chau nova','adios','hasta luego','hasta pronto','nos vemos','me voy','cerrar sesion','salir'].includes(social))return {...result('¡Hasta luego! Tu sesión quedó cerrada.',{}),cerrar_sesion:true};
 if(['cancelar','cancela','dejalo','olvidalo','no quiero seguir'].includes(social))return result('Listo, cancelé esta consulta. ¿En qué más puedo ayudarte?',base,MENU);
 if(['hola','hola nova','buen dia','buenas','buenas tardes','buenas noches','hey'].includes(social))return result((p?`¡Hola, ${p.nombre}!`:'¡Hola! Soy Nova.')+(step?' Seguimos con tu consulta; también podés escribir cancelar.':' Podés consultar productos o cotizar un préstamo, aunque no seas cliente.'),s,step?[]:MENU);
 if(['gracias','muchas gracias','genial','perfecto','joya','buenisimo'].includes(social))return result('¡De nada! Acá estoy si necesitás algo más.',s);
 if(['ayuda','que podes hacer','como funciona','en que me ayudas'].includes(social))return result('Puedo contarte sobre cuentas y tarjetas, cotizar un PP y consultar saldo, alias, TC, TD y transferencias con un DNI de prueba. Escribí cancelar para dejar una consulta.',s,MENU);
 if(['no soy cliente','soy visitante','continuar como visitante','seguir como visitante','no tengo cuenta'].includes(social)){
  if(['monto','cuotas'].includes(step))return advanceLoan('',Object.fromEntries(['paso','monto','cuotas'].filter(k=>k in s).map(k=>[k,s[k]])));
  return result('¡Podés consultar igual! Conocé nuestros productos o cotizá un préstamo sin ingresar un DNI.',{},MENU.slice(0,3));
 }
 if(['clientes de prueba','ver clientes de prueba','mostrar clientes de prueba'].includes(social))return result('Elegí uno de estos perfiles ficticios:\n'+Object.entries(CLIENTES).map(([dni,c])=>`${dni} · ${c.nombre}`).join('\n'),s,Object.keys(CLIENTES));
 if(['soy cliente','entrar a mi cuenta','iniciar sesion','cambiar cliente'].includes(social))return result('Ingresá un DNI de prueba de 8 dígitos. Voy a mostrarte la evaluación crediticia del perfil con datos ficticios. No se consulta ninguna central externa ni se guarda la información en una base de datos; se elimina al cerrar la sesión.',{paso:'identificar'},['Ver clientes de prueba','Continuar como visitante']);
 if(/^\d{8}$/.test(message.trim())&&!['monto','cuotas','ingreso'].includes(step)){
  const next={dni:message.trim()},name=profile(next).nombre,report=evaluation(next);
  if(step==='evaluacion_dni')return result(`¡Hola, ${name}!\n${report}\n\nPara evaluar el préstamo de ${money(s.ultimo_prestamo)}, ¿cuál es tu ingreso mensual neto de prueba?`,{...next,paso:'ingreso',ultimo_prestamo:s.ultimo_prestamo,ultimas_cuotas:s.ultimas_cuotas},['Cancelar']);
  if(s.pendiente){const a=respond(s.pendiente,next);a.texto=`¡Hola, ${name}!\n${report}\n\n`+a.texto;return a}
  return result(`¡Hola, ${name}!\n${report}\n\n¿Qué querés consultar?`,next,['Consultar saldo','Mi score','Mi TC','Cotizar un préstamo']);
 }
 if(['evaluar mi prestamo','solicitar prestamo','pedir este prestamo'].includes(social)&&s.ultimo_prestamo){const application={...base,ultimo_prestamo:s.ultimo_prestamo,ultimas_cuotas:s.ultimas_cuotas};if(p)return result('Para calcular la tasa de tu perfil y evaluar la solicitud, ¿cuál es tu ingreso mensual neto de prueba?',{...application,paso:'ingreso'},['Cancelar']);return result('Para calcular tu tasa y evaluar el préstamo, ingresá un DNI de prueba de 8 dígitos o elegí un perfil. No consultamos centrales externas ni guardamos el DNI en una base de datos.',{...application,paso:'evaluacion_dni'},['Ver clientes de prueba','Cancelar'])}
 if(step==='ingreso'){const [income]=parseLoan(message);if(income===null||income<100000||income>50000000)return result('Ingresá un ingreso mensual neto de prueba entre $100.000 y $50.000.000. Por ejemplo, “800 mil”.',s,['Cancelar']);return assessLoan(s,income)}
 if(step==='evaluacion_dni')return result('Para evaluar el préstamo necesito un DNI de prueba de 8 dígitos. También podés elegir uno de la lista.',s,['Ver clientes de prueba','Cancelar']);
 const intent=classify(message);
 if(PUBLICAS[intent])return result(PUBLICAS[intent],['monto','cuotas'].includes(step)?s:base,['Cotizar un préstamo','Soy cliente','Ver clientes de prueba']);
 if(s.ultimo_prestamo&&/mejor|cambiar|eran|equivoque|\by en\b/.test(t)){
  let [monto,cuotas]=parseLoan(message);const en=t.match(/\ben\s+(6|12|24)\b/);if(cuotas===null&&en){cuotas=Number(en[1]);monto=null}
  return advanceLoan(cuotas===null||monto?message:`${cuotas} cuotas`,{...base,paso:'cuotas',monto:s.ultimo_prestamo,cuotas:s.ultimas_cuotas});
 }
 if(['monto','cuotas'].includes(step)&&!PERSONALES.includes(intent))return advanceLoan(message,s);
 if(intent==='prestamo')return advanceLoan(message,base);
 if(step==='tipo_tarjeta'){
  const tipo=has(t,'td')||has(t,'debito')?'td':has(t,'tc')||has(t,'credito')?'tc':null;
  if(tipo)return result(`Tu tarjeta de ${tipo==='td'?'débito':'crédito'} quedó bloqueada en este perfil. Gestión NX-2048.`,{...base,bloqueadas:[...new Set([...(base.bloqueadas||[]),tipo])]});
  if(!PERSONALES.includes(intent))return result('¿Querés bloquear la tarjeta de débito (TD) o crédito (TC)?',s,['Débito (TD)','Crédito (TC)','Cancelar']);
 }
 if(PERSONALES.includes(intent)&&!p)return result('Para consultar tus productos necesito identificar un perfil. Ingresá un DNI de prueba o elegí uno de la lista. La evaluación crediticia usa datos ficticios, sin consultar una central externa. El DNI se mantiene solo durante la sesión y no se guarda en una base de datos.',{paso:'identificar',pendiente:message},['Ver clientes de prueba','Continuar como visitante','Soy cliente']);
 if(intent==='tarjeta_perdida')return result('Te ayudo a bloquearla. ¿Es de débito (TD) o crédito (TC)?',{...base,paso:'tipo_tarjeta'},['Débito (TD)','Crédito (TC)','Cancelar']);
 if(p){
  const today=new Date();today.setHours(0,0,0,0);const vence=new Date(today.getFullYear(),today.getMonth(),p.dia);if(vence<today)vence.setMonth(vence.getMonth()+1);const cierre=new Date(vence);cierre.setDate(cierre.getDate()-10);const yesterday=new Date(today);yesterday.setDate(yesterday.getDate()-1);const fecha=formatDate(yesterday),td=base.bloqueadas?.includes('td')?'bloqueada':'activa',tc=base.bloqueadas?.includes('tc')?'bloqueada':'activa';
  const texts={score:evaluation(s),saldo:`Tu caja de ahorro tiene ${money(p.saldo)} disponibles.`,tc:`Tu tarjeta de crédito está ${tc}.\nLímite total: ${money(p.limite_tc)}\nConsumos del resumen: ${money(p.tc)}\nCierre: ${formatDate(cierre)}\nVencimiento: ${formatDate(vence)}\nDisponible para compras: ${money(p.limite_tc-p.tc)}.`,td:`Tu tarjeta de débito está ${td} y usa el saldo de tu caja de ahorro: ${money(p.saldo)}.`,alias:`Alias de prueba: buainco.${s.dni}\nCBU ficticio: 00000000${s.dni}000000\nTitular del perfil: ${p.nombre}.`,transferencia:`Última transferencia\nDestinatario: Alex Ríos\nImporte: ${money(p.transferencia)}\nFecha: ${fecha}\nEstado: completada\nComprobante: BUA-${s.dni.slice(-4)}-01.`};
  if(texts[intent])return result(texts[intent],base);
 }
 if(step==='identificar')return result('Necesito un DNI de prueba de 8 dígitos para esta consulta personal. Si preferís, seguimos como visitante.',s,['Ver clientes de prueba','Continuar como visitante']);
 return result('No llegué a entender. Podés preguntarme por cuentas, tarjetas, préstamos o asesores. Por ejemplo: “¿qué productos tienen?” o “quiero 300 mil en 12 cuotas”.',base,MENU);
}
function localAnswer(message){const a=respond(message,state);state=a.estado;return a}
