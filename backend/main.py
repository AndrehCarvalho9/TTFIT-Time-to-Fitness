from datetime import date
from pathlib import Path
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB = Path(__file__).resolve().parent / 'ttfit.db'
app = FastAPI(title='TTFIT API', description='API inicial do TTFIT. Dados nutricionais demonstrativos.', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*']) # Apenas desenvolvimento local.
SEED=[('Arroz cozido',130,2.7,28.2,.3),('Feijão cozido',76,4.8,13.6,.5),('Peito de frango grelhado',165,31,0,3.6),('Ovo cozido',155,13,1.1,11),('Banana',89,1.1,22.8,.3),('Aveia',389,16.9,66.3,6.9)]
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c
def init():
 with db() as c:
  c.execute('CREATE TABLE IF NOT EXISTS foods(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE NOT NULL,calories_100g REAL NOT NULL,protein_100g REAL NOT NULL,carbs_100g REAL NOT NULL,fat_100g REAL NOT NULL)')
  c.execute('CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY AUTOINCREMENT,food_id INTEGER NOT NULL,grams REAL NOT NULL CHECK(grams>0),entry_date TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(food_id) REFERENCES foods(id))')
  if c.execute('SELECT COUNT(*) FROM foods').fetchone()[0]==0:c.executemany('INSERT INTO foods(name,calories_100g,protein_100g,carbs_100g,fat_100g) VALUES(?,?,?,?,?)',SEED)
@app.on_event('startup')
def startup():init()
class NewEntry(BaseModel):food_id:int;grams:float=Field(gt=0,le=3000)
def serialize(r):
 f=r['grams']/100
 return {'id':r['id'],'food_id':r['food_id'],'food_name':r['food_name'],'grams':r['grams'],'calories':round(r['calories_100g']*f,2),'protein_g':round(r['protein_100g']*f,2),'carbs_g':round(r['carbs_100g']*f,2),'fat_g':round(r['fat_100g']*f,2),'entry_date':r['entry_date']}
QUERY='SELECT e.id,e.food_id,e.grams,e.entry_date,f.name AS food_name,f.calories_100g,f.protein_100g,f.carbs_100g,f.fat_100g FROM entries e JOIN foods f ON f.id=e.food_id'
@app.get('/')
def root():return {'app':'TTFIT API','docs':'/docs'}
@app.get('/api/health')
def health():return {'status':'ok'}
@app.get('/api/foods')
def foods():
 with db() as c:rows=c.execute('SELECT * FROM foods ORDER BY name').fetchall()
 return [dict(r) for r in rows]
@app.get('/api/entries')
def get_entries():
 with db() as c:rows=c.execute(QUERY+' WHERE e.entry_date=? ORDER BY e.id DESC',(date.today().isoformat(),)).fetchall()
 return [serialize(r) for r in rows]
@app.post('/api/entries',status_code=201)
def add_entry(payload:NewEntry):
 with db() as c:
  if not c.execute('SELECT id FROM foods WHERE id=?',(payload.food_id,)).fetchone():raise HTTPException(404,'Alimento não encontrado.')
  cur=c.execute('INSERT INTO entries(food_id,grams,entry_date) VALUES(?,?,?)',(payload.food_id,payload.grams,date.today().isoformat()))
  r=c.execute(QUERY+' WHERE e.id=?',(cur.lastrowid,)).fetchone()
 return serialize(r)
@app.delete('/api/entries/{entry_id}',status_code=204)
def delete_entry(entry_id:int):
 with db() as c:
  cur=c.execute('DELETE FROM entries WHERE id=? AND entry_date=?',(entry_id,date.today().isoformat()))
  if cur.rowcount==0:raise HTTPException(404,'Registro não encontrado.')
@app.delete('/api/entries',status_code=204)
def clear_entries():
 with db() as c:c.execute('DELETE FROM entries WHERE entry_date=?',(date.today().isoformat(),))
