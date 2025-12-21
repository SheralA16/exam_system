# 🚀 GUÍA DE DEPLOYMENT - SISTEMA DE EXÁMENES USS

## 📋 RESUMEN
Esta guía te llevará paso a paso para publicar tu Sistema de Exámenes en **Render.com + Cloudinary** completamente **GRATIS**.

---

## ✅ PREREQUISITOS

- [ ] Cuenta de GitHub (crear en https://github.com)
- [ ] Cuenta de Render (crear en https://render.com)
- [ ] Cuenta de Cloudinary (crear en https://cloudinary.com)
- [ ] Git instalado en tu computadora

---

## 🔧 PASO 1: CONFIGURAR CLOUDINARY (5 minutos)

### 1.1 Crear cuenta en Cloudinary
1. Ve a https://cloudinary.com
2. Haz clic en "Sign Up Free"
3. Completa el registro (puedes usar tu email o GitHub)
4. Verifica tu email

### 1.2 Obtener credenciales
1. Una vez dentro, ve al **Dashboard**
2. Encontrarás estas credenciales (¡guárdalas!):
   ```
   Cloud Name: tu_cloud_name
   API Key: tu_api_key
   API Secret: tu_api_secret
   ```

✅ **Listo:** Ya tienes 25 GB gratis para imágenes

---

## 📦 PASO 2: SUBIR TU PROYECTO A GITHUB (10 minutos)

### 2.1 Crear repositorio en GitHub
1. Ve a https://github.com/new
2. Nombre del repositorio: `exam-system-uss` (o el que prefieras)
3. Selecciona: **Public**
4. **NO marques** "Add a README file"
5. Haz clic en "Create repository"

### 2.2 Subir tu código
Abre la terminal en la carpeta de tu proyecto y ejecuta:

```bash
# Inicializar Git (si no lo has hecho)
git init

# Agregar todos los archivos
git add .

# Hacer el primer commit
git commit -m "Preparar proyecto para deployment en Render"

# Conectar con GitHub (reemplaza TU-USUARIO y TU-REPO)
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git

# Subir el código
git branch -M main
git push -u origin main
```

✅ **Listo:** Tu código está en GitHub

---

## 🚀 PASO 3: DEPLOYMENT EN RENDER (15 minutos)

### 3.1 Crear cuenta en Render
1. Ve a https://render.com
2. Haz clic en "Get Started"
3. Registra con tu cuenta de GitHub (recomendado)
4. Autoriza a Render para acceder a tus repositorios

### 3.2 Crear Base de Datos PostgreSQL
1. En el Dashboard de Render, haz clic en **"New +"**
2. Selecciona **"PostgreSQL"**
3. Configuración:
   - **Name:** `exam-system-db`
   - **Database:** `exam_system_db`
   - **User:** `exam_system_user`
   - **Region:** Oregon (US West) - el más cercano
   - **Plan:** **FREE**
4. Haz clic en **"Create Database"**
5. **ESPERA** unos minutos hasta que el estado sea "Available"
6. Copia la **Internal Database URL** (la necesitarás)

### 3.3 Crear Web Service
1. Haz clic en **"New +"** nuevamente
2. Selecciona **"Web Service"**
3. Conecta tu repositorio de GitHub:
   - Busca `exam-system-uss` (o el nombre que usaste)
   - Haz clic en "Connect"

4. Configuración del servicio:
   - **Name:** `exam-system-uss`
   - **Region:** Oregon (US West)
   - **Branch:** `main`
   - **Root Directory:** (dejar vacío)
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn exam_system.wsgi:application`
   - **Plan:** **FREE**

5. **Variables de Entorno** (Environment Variables):
   Haz clic en "Advanced" y agrega estas variables:

   | Key | Value |
   |-----|-------|
   | `DEBUG` | `False` |
   | `SECRET_KEY` | (genera uno nuevo en https://djecrety.ir/) |
   | `DATABASE_URL` | (pega la Internal Database URL que copiaste) |
   | `ALLOWED_HOSTS` | `exam-system-uss.onrender.com` (usa tu URL) |
   | `CLOUDINARY_CLOUD_NAME` | (tu cloud name de Cloudinary) |
   | `CLOUDINARY_API_KEY` | (tu api key de Cloudinary) |
   | `CLOUDINARY_API_SECRET` | (tu api secret de Cloudinary) |

6. Haz clic en **"Create Web Service"**

### 3.4 Esperar el Deploy
- Render comenzará a construir tu aplicación
- Verás los logs en tiempo real
- El primer deploy toma **5-10 minutos**
- Cuando veas "Build successful", ¡está listo!

✅ **Listo:** Tu sitio está en línea en `https://exam-system-uss.onrender.com`

---

## 🔐 PASO 4: CREAR SUPERUSUARIO (5 minutos)

### 4.1 Acceder a la Shell de Render
1. En el Dashboard de tu Web Service
2. Ve a la pestaña **"Shell"** en el menú izquierdo
3. Haz clic en **"Launch Shell"**
4. Espera a que se abra la terminal

### 4.2 Crear el superusuario
En la shell que se abrió, ejecuta:

```bash
python manage.py createsuperuser
```

Completa la información:
- Username: admin
- Email: tu@email.com
- Password: (tu contraseña segura)

✅ **Listo:** Ya puedes acceder al admin en `https://tu-sitio.onrender.com/admin/`

---

## 🧪 PASO 5: VERIFICAR QUE TODO FUNCIONE

### 5.1 Acceder a tu sitio
1. Ve a `https://exam-system-uss.onrender.com` (tu URL)
2. Deberías ver la página de login

### 5.2 Probar funcionalidades
- [ ] Login funciona
- [ ] Dashboard de admin carga
- [ ] Puedes crear un curso
- [ ] Puedes subir una imagen (se guarda en Cloudinary)
- [ ] Puedes crear usuarios
- [ ] Puedes crear exámenes

✅ **Si todo funciona:** ¡FELICIDADES! Tu sitio está en producción

---

## ⚠️ IMPORTANTE: LIMITACIONES DEL PLAN FREE

### Render Free Tier:
- ✅ El sitio se "duerme" después de 15 minutos sin actividad
- ✅ Tarda ~30 segundos en "despertar" la primera vez
- ✅ 750 horas/mes (suficiente para uso normal)
- ✅ Base de datos: 90 días de retención, luego se elimina si no hay actividad

### Cloudinary Free Tier:
- ✅ 25 GB de almacenamiento
- ✅ 25 GB de ancho de banda/mes
- ✅ Permanente

### Recomendación:
- Visita tu sitio al menos una vez cada 60 días para que la base de datos no se elimine
- Si necesitas que el sitio esté siempre activo, considera upgrading a plan pagado ($7/mes)

---

## 🔄 PASO 6: ACTUALIZAR TU SITIO (Futuras Modificaciones)

Cuando hagas cambios en tu código local:

```bash
# 1. Guardar cambios
git add .
git commit -m "Descripción de los cambios"

# 2. Subir a GitHub
git push origin main

# 3. Render detectará los cambios y hará deploy automático
```

✅ **Render hace deploy automático** cada vez que pusheas a GitHub

---

## 📞 SOPORTE Y AYUDA

### Si algo sale mal:

1. **Revisa los logs en Render:**
   - Dashboard → Tu servicio → "Logs"

2. **Errores comunes:**
   - **500 Error:** Revisa las variables de entorno
   - **404 en admin:** Verifica ALLOWED_HOSTS
   - **Imágenes no cargan:** Verifica credenciales de Cloudinary

3. **Render Docs:** https://render.com/docs/deploy-django
4. **Cloudinary Docs:** https://cloudinary.com/documentation/django_integration

---

## 🎉 ¡FELICIDADES!

Tu Sistema de Exámenes USS ya está en producción y accesible desde cualquier parte del mundo.

**URL de tu sitio:** `https://exam-system-uss.onrender.com`

### Próximos pasos recomendados:
- [ ] Configurar un dominio personalizado (opcional)
- [ ] Habilitar backups de la base de datos
- [ ] Monitorear el uso de Cloudinary
- [ ] Agregar más funcionalidades

---

## 📝 NOTAS ADICIONALES

### Generar nuevo SECRET_KEY
Si necesitas generar un nuevo SECRET_KEY seguro:
1. Ve a https://djecrety.ir/
2. Copia la key generada
3. Actualízala en las variables de entorno de Render

### Cambiar a dominio personalizado
Render permite dominios personalizados en el plan free:
1. Compra un dominio en Namecheap, GoDaddy, etc.
2. En Render: Settings → Custom Domain
3. Sigue las instrucciones para configurar el DNS

### Backup de Base de Datos
Render hace backups automáticos, pero para mayor seguridad:
```bash
# Desde la Shell de Render
python manage.py dumpdata > backup.json
```

---

**Autor:** Sistema de Exámenes USS
**Fecha:** Diciembre 2025
**Versión:** 1.0
