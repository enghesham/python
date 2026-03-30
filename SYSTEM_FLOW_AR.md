# شرح فلو المشروع

هذا الملف يشرح كيف يشتغل مشروع `Task Manager` الحالي ملفًا ملفًا، وما هو مسار التنفيذ من أول أمر التشغيل حتى الوصول إلى قاعدة البيانات.

## 1. الفكرة العامة

المشروع مبني بأسلوب `Clean Architecture` بشكل مبسط:

- `presentation`
  تستقبل الأوامر من المستخدم.
- `application`
  تحتوي use cases التي تنفذ منطق التطبيق.
- `domain`
  تحتوي الكيانات الأساسية والعقود `contracts`.
- `infrastructure`
  تحتوي تفاصيل التنفيذ الفعلية مثل `SQLAlchemy` و`SQLite`.

الفكرة المهمة هنا:

- الـ `CLI` لا يعرف تفاصيل SQLAlchemy.
- الـ `Use Cases` لا تعرف كيف يتم تخزين البيانات.
- الـ `Repository` هو الجسر بين منطق التطبيق وطبقة قاعدة البيانات.

## 2. الفلو العام من البداية للنهاية

عندما تشغل أمر مثل:

```bash
python main.py add "Write docs" --description "Document architecture"
```

الفلو يكون كالتالي:

1. الملف `main.py` يشتغل كنقطة دخول.
2. يستدعي `main()` الموجود داخل `app/presentation/cli.py`.
3. `cli.py` يقرأ الأمر من المستخدم بواسطة `argparse`.
4. `cli.py` ينشئ الإعدادات والـ repository من خلال `app/bootstrap.py`.
5. `bootstrap.py` ينشئ `SqliteDatabase`.
6. `SqliteDatabase` ينشئ `SQLAlchemy engine` و`session factory` ويتأكد أن الجدول موجود.
7. `bootstrap.py` يعيد `SqliteTaskRepository`.
8. `cli.py` يمرر الـ repository إلى الـ use case المناسب.
9. الـ use case ينفذ منطق التطبيق.
10. الـ repository ينفذ القراءة أو الكتابة على قاعدة البيانات عبر `SQLAlchemy`.
11. النتيجة ترجع إلى `cli.py`.
12. `cli.py` يطبع النتيجة للمستخدم.

## 3. شرح ملف ملف

### `main.py`

المسؤولية:

- نقطة الدخول الرئيسية للمشروع.
- لا يحتوي منطق أعمال.
- فقط يحول التنفيذ إلى `app.presentation.cli.main`.

ماذا يفعل:

- عند تشغيل `python main.py` ينفذ `main()` من طبقة العرض.

### `app/config.py`

المسؤولية:

- تعريف الإعدادات الافتراضية للتطبيق.

ماذا يحتوي:

- `database_path`
  المسار الافتراضي لقاعدة البيانات: `data/tasks.db`
- `legacy_json_path`
  المسار الافتراضي لملف JSON القديم: `data/tasks.json`

الفائدة:

- فصل الإعدادات عن منطق التشغيل.
- لاحقًا في `FastAPI` يمكن تحميل نفس الإعدادات من env vars أو config file بسهولة.

### `app/bootstrap.py`

المسؤولية:

- ربط مكونات المشروع ببعضها.
- هذا الملف هو نقطة الـ wiring أو الـ dependency composition.

ماذا يفعل:

- يبني `AppSettings`
- يبني `SqliteDatabase`
- يبني `SqliteTaskRepository`

لماذا مهم:

- عند الانتقال إلى `FastAPI` سنعيد استخدام نفس الفكرة بدل بناء المكونات داخل كل route.

### `app/domain/entities/task.py`

المسؤولية:

- تعريف كيان المهمة `Task`.

ماذا يحتوي:

- `id`
- `title`
- `description`
- `status`
- `created_at`
- `updated_at`

منطق داخلي مهم:

- `__post_init__`
  تنظف العنوان والوصف وتمنع إنشاء task بعنوان فارغ.
- `mark_done`
  تغيّر الحالة إلى `done` وتحدث `updated_at`.

هذا الملف يمثل الـ business object الأساسي.

### `app/domain/repositories/task_repository.py`

المسؤولية:

- تعريف العقد `contract` الذي يجب أن يلتزم به أي repository.

المتوفر فيه:

- `add`
- `list_all`
- `get_by_id`
- `update`
- `delete`

الفائدة:

- الـ use cases تتعامل مع abstraction وليس مع SQLAlchemy مباشرة.
- يمكن لاحقًا استبدال SQLite بـ PostgreSQL أو API خارجي بدون تعديل الـ use cases.

### `app/application/exceptions.py`

المسؤولية:

- تعريف الأخطاء الخاصة بالتطبيق.

الموجود:

- `TaskManagerError`
- `TaskNotFoundError`

الفائدة:

- توحيد الأخطاء داخل التطبيق.
- طبقة العرض تتعامل معها وتعرض رسالة مناسبة.

### `app/application/use_cases/create_task.py`

المسؤولية:

- إنشاء مهمة جديدة.

الفلو:

1. يستقبل `title` و`description`
2. ينشئ `Task`
3. يرسلها إلى `repository.add`
4. يعيد الـ task الناتجة

### `app/application/use_cases/list_tasks.py`

المسؤولية:

- إرجاع كل المهام.

الفلو:

1. يطلب من `repository.list_all()`
2. يعيد قائمة المهام

### `app/application/use_cases/complete_task.py`

المسؤولية:

- تعليم task على أنها منجزة.

الفلو:

1. يبحث عن المهمة عبر `repository.get_by_id`
2. إذا لم يجدها يرمي `TaskNotFoundError`
3. إذا وجدها ينفذ `task.mark_done()`
4. يرسل النسخة المعدلة إلى `repository.update`

### `app/application/use_cases/delete_task.py`

المسؤولية:

- حذف مهمة.

الفلو:

1. يطلب من `repository.delete(task_id)`
2. إذا أعاد `False` فهذا يعني أن المهمة غير موجودة
3. يرمي `TaskNotFoundError`

### `app/application/use_cases/migrate_tasks.py`

المسؤولية:

- ترحيل البيانات من مصدر قديم إلى مصدر جديد.

الحالة الحالية:

- من `JsonTaskRepository` إلى `SqliteTaskRepository`

الفلو:

1. يقرأ كل المهام من المصدر القديم
2. يفحص إذا كانت موجودة مسبقًا في الوجهة
3. يضيف غير الموجود
4. يرجع عدد المهام التي تم ترحيلها

### `app/presentation/cli.py`

المسؤولية:

- قراءة أوامر المستخدم من الـ terminal.
- ربط كل command بالـ use case المناسب.

الأوامر المدعومة:

- `init-db`
- `add`
- `list`
- `complete`
- `delete`
- `migrate-json`

كيف يعمل:

1. يبني parser
2. يقرأ arguments
3. يبني settings
4. يبني repository
5. يختار handler حسب الأمر
6. ينفذ العملية
7. يطبع النتيجة
8. يغلق الـ repository إذا كان يملك `close()`

### `app/infrastructure/database/sqlite.py`

المسؤولية:

- إنشاء `SQLAlchemy engine`
- إنشاء `session factory`
- تهيئة قاعدة البيانات
- إدارة lifecycle للـ session

ماذا يفعل:

- يبني engine على `sqlite:///...`
- يستدعي `Base.metadata.create_all(...)`
- يوفّر `session()` كـ context manager

داخل `session()`:

1. يفتح session
2. ينفذ العملية
3. يعمل `commit` إذا نجحت
4. يعمل `rollback` إذا فشلت
5. يغلق session دائمًا

### `app/infrastructure/database/models.py`

المسؤولية:

- تعريف موديلات SQLAlchemy.

الموجود:

- `Base`
- `TaskModel`

`TaskModel` هو الشكل الذي يُخزَّن داخل قاعدة البيانات.

الأعمدة الحالية:

- `id`
- `title`
- `description`
- `status`
- `created_at`
- `updated_at`

### `app/infrastructure/persistence/sqlite_task_repository.py`

المسؤولية:

- تنفيذ `TaskRepository` باستخدام `SQLAlchemy`.

ماذا يفعل:

- `add`
  يحول `Task` إلى `TaskModel` ثم يعمل `session.add`
- `list_all`
  ينفذ `select(TaskModel)` ويرجع Entities
- `get_by_id`
  يستخدم `session.get`
- `update`
  يقرأ السجل ويعدل الحقول
- `delete`
  يقرأ السجل ثم يحذفه
- `close`
  يغلق engine عبر طبقة قاعدة البيانات

الفكرة الأساسية:

- الـ domain entity لا تدخل قاعدة البيانات مباشرة.
- نعمل mapping بين:
  `Task <-> TaskModel`

### `app/infrastructure/persistence/json_task_repository.py`

المسؤولية:

- التخزين القديم المعتمد على `JSON`.

لماذا ما زال موجودًا:

- حتى نستخدمه فقط في migration من `tasks.json` إلى `tasks.db`.

### `tests/test_task_manager.py`

المسؤولية:

- اختبار الفلو الأساسي للمشروع.

ما الذي يتم اختباره:

- إنشاء مهمة
- قراءة المهام
- إنهاء مهمة
- حذف مهمة
- التعامل مع مهمة غير موجودة
- إضافة مهمة من خلال CLI
- ترحيل مهام من JSON إلى SQLite

## 4. شرح الأوامر

### تهيئة قاعدة البيانات

```bash
python main.py init-db
```

ماذا يحدث:

1. `cli.py` يبني repository
2. `SqliteDatabase` ينشئ الـ engine
3. `Base.metadata.create_all()` ينشئ جدول `tasks` إذا لم يكن موجودًا

### إضافة مهمة

```bash
python main.py add "Write docs" --description "Document architecture"
```

ماذا يحدث:

1. `cli.py` يختار `_handle_add`
2. `CreateTaskUseCase.execute(...)`
3. إنشاء `Task`
4. `repository.add(task)`
5. SQLAlchemy يعمل `INSERT`
6. CLI يطبع:
   `Created task <id>: Write docs`

### عرض المهام

```bash
python main.py list
```

ماذا يحدث:

1. `cli.py` يختار `_handle_list`
2. `ListTasksUseCase.execute()`
3. `repository.list_all()`
4. SQLAlchemy يعمل `SELECT`
5. تتحول النتائج إلى `Task entities`
6. CLI يطبع كل task

### إنهاء مهمة

```bash
python main.py complete <task-id>
```

ماذا يحدث:

1. `CompleteTaskUseCase` يقرأ المهمة
2. ينفذ `mark_done()`
3. `repository.update(task)`
4. SQLAlchemy يعمل `UPDATE`

### حذف مهمة

```bash
python main.py delete <task-id>
```

ماذا يحدث:

1. `DeleteTaskUseCase` يطلب الحذف
2. repository يفحص وجود السجل
3. SQLAlchemy يعمل `DELETE`
4. إذا المهمة غير موجودة يتم رفع `TaskNotFoundError`

### ترحيل JSON إلى قاعدة البيانات

```bash
python main.py migrate-json
```

أو:

```bash
python main.py --legacy-json data/tasks.json --database data/tasks.db migrate-json
```

ماذا يحدث:

1. `cli.py` يبني repository الجديد الخاص بقاعدة البيانات
2. ينشئ `JsonTaskRepository` للملف القديم
3. `MigrateTasksUseCase` يقرأ من JSON
4. يفحص الوجود في SQLite
5. يضيف غير الموجود
6. يطبع عدد العناصر التي تم نقلها

## 5. أين سندخل FastAPI لاحقًا

المدخل الصحيح للـ `FastAPI` سيكون فوق الطبقات الحالية، وليس بدلها.

يعني:

- `FastAPI routes` ستدخل في طبقة presentation الجديدة
- routes ستستدعي نفس الـ use cases الحالية
- dependency injection في `FastAPI` سيستفيد من `bootstrap.py`
- repository الحالي سيبقى كما هو

الشكل المتوقع لاحقًا:

1. request يدخل من API route
2. route تستدعي use case
3. use case تستدعي repository
4. repository يتعامل مع SQLAlchemy
5. response يرجع JSON للعميل

## 6. أهم الملفات التي تبدأ منها إذا أردت الفهم بسرعة

إذا أردت تقرأ المشروع بترتيب منطقي:

1. `main.py`
2. `app/presentation/cli.py`
3. `app/bootstrap.py`
4. `app/application/use_cases/create_task.py`
5. `app/application/use_cases/complete_task.py`
6. `app/domain/entities/task.py`
7. `app/domain/repositories/task_repository.py`
8. `app/infrastructure/persistence/sqlite_task_repository.py`
9. `app/infrastructure/database/sqlite.py`
10. `app/infrastructure/database/models.py`

## 7. أوامر مفيدة لك الآن

تشغيل وإنشاء الجدول:

```bash
python main.py init-db
```

إضافة مهمة:

```bash
python main.py add "Study FastAPI" --description "Prepare API layer"
```

عرض المهام:

```bash
python main.py list
```

إنهاء مهمة:

```bash
python main.py complete <task-id>
```

حذف مهمة:

```bash
python main.py delete <task-id>
```

ترحيل البيانات القديمة:

```bash
python main.py migrate-json
```

تشغيل الاختبارات:

```bash
python -m unittest discover -s tests
```

## 8. الخلاصة

الفلو الحالي نظيف وواضح:

- `CLI` تستقبل الأوامر
- `Use Cases` تطبق منطق التطبيق
- `Repository Contract` يفصل المنطق عن التخزين
- `SQLAlchemy Repository` ينفذ التخزين الفعلي
- `SQLite` هي قاعدة البيانات الحالية

هذا يعني أن المشروع الآن جاهز جدًا للخطوة القادمة: بناء `FastAPI` فوق نفس الطبقات بدون إعادة كتابة المنطق الأساسي.
