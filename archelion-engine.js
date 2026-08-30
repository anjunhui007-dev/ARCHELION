/* Deterministic ARCHELION rules. Narrative services must not alter these formulas. */
window.ARCHELION = (() => {
  const MAX_LEVEL=70, order=['C1','C2','C3','C4','C5'], clamp=(n,a,b)=>Math.max(a,Math.min(b,n)), num=v=>Number(v)||0;
  const CHESTS={
    C1:{name:'낡은 상자',slots:2,contents:{gold:35,material:30,consumable:20,equipment:12,elixir:1,mystery:2},grades:{'일반':70,'고급':25,'희귀':5,'영웅':0,'전설':0,'고유':0},gold:[20,60]},
    C2:{name:'견고한 상자',slots:3,contents:{gold:28,material:25,consumable:20,equipment:20,elixir:3,mystery:4},grades:{'일반':40,'고급':42,'희귀':16,'영웅':2,'전설':0,'고유':0},gold:[50,150]},
    C3:{name:'화려한 상자',slots:4,contents:{gold:20,material:19,consumable:18,equipment:30,elixir:6,mystery:7},grades:{'일반':15,'고급':40,'희귀':35,'영웅':9,'전설':1,'고유':0},gold:[120,350]},
    C4:{name:'찬란한 상자',slots:5,contents:{gold:14,material:13,consumable:15,equipment:40,elixir:10,mystery:8},grades:{'일반':3,'고급':22,'희귀':45,'영웅':25,'전설':5,'고유':0},gold:[300,800]},
    C5:{name:'전설의 상자',slots:6,contents:{gold:8,material:8,consumable:10,equipment:50,elixir:14,mystery:10},grades:{'일반':0,'고급':8,'희귀':37,'영웅':38,'전설':15,'고유':2},gold:[700,2000]}
  };
  function slots(level){return Math.min(15,1+Math.floor((Math.max(1,num(level))-1)/3))}
  function resources(vitality){const e=Math.max(0,num(vitality)-5);return{maxHp:100+e*4,maxSp:100+e*2}}
  function damage({kind='physical',stats={},attackBase=5,physicalDefense=0,magicDefense=0,penetration=0,crit=false,critDamage=150}){let raw=kind==='magic'?attackBase+num(stats.mana)*.8+num(stats.intelligence)*.4:kind==='fixed'?attackBase:attackBase+num(stats.strength)+num(stats.agility)*.3;if(crit)raw*=num(critDamage)/100;if(kind==='fixed')return Math.max(0,raw);const defense=Math.max(0,(kind==='magic'?num(magicDefense):num(physicalDefense))-num(penetration));return Math.max(0,raw*100/(100+defense))}
  function roll(table,rng=Math.random){let x=rng()*100;for(const[k,v]of Object.entries(table)){x-=v;if(x<0)return k}return Object.keys(table).at(-1)}
  function chest(base='C1',rareRate=0,rng=Math.random){let i=order.indexOf(base);if(i<0)i=0;const before=order[i];if(i<4&&rng()*100<clamp(num(rareRate),0,100))i++;const id=order[i],data=CHESTS[id],rewards=[];for(let x=0;x<data.slots;x++)rewards.push(roll(data.contents,rng));return{id,before,upgraded:id!==before,slots:data.slots,rewards,goldRange:data.gold,gradeTable:data.grades}}
  return{MAX_LEVEL,CHESTS,slots,resources,damage,chest,clamp};
})();
