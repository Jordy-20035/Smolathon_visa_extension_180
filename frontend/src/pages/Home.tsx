import React, { useState, useEffect } from "react";
import { ChevronRight, Phone, Mail, MapPin, Clock, Users, Shield, Heart, Zap, ArrowRight, Calendar, Star, CheckCircle } from "lucide-react";
import logo from "../assets/logo.jpg"; // adjust path if needed


// Enhanced data with more engaging content
const team = [
  { 
    name: "Алексей Иванов", 
    role: "Руководитель отдела безопасности дорожного движения",
    experience: "15 лет опыта",
    achievements: "Снижение ДТП на 40%"
  },
  { 
    name: "Мария Петрова", 
    role: "Специалист по анализу транспортных потоков",
    experience: "8 лет опыта", 
    achievements: "Оптимизация 150+ перекрестков"
  },
  { 
    name: "Дмитрий Соколов", 
    role: "Инженер дорожного хозяйства",
    experience: "12 лет опыта",
    achievements: "200+ реализованных проектов"
  },
];

const projects = [
  { 
    title: "Безопасные пешеходные переходы", 
    description: "Современные светофорные объекты с тактильными элементами для людей с ограниченными возможностями. Установлено 45 новых переходов.",
    icon: "🚶",
    status: "Завершено",
    impact: "Снижение ДТП на 35%"
  },
  { 
    title: "Умные светофоры", 
    description: "Адаптивная система регулирования с искусственным интеллектом. Сокращение времени ожидания до 40%.",
    icon: "🚦",
    status: "В процессе",
    impact: "60 установленных систем"
  },
  { 
    title: "Народный контроль", 
    description: "Мобильное приложение для быстрого сообщения о проблемах. Уже решено более 1000 обращений граждан.",
    icon: "📱",
    status: "Активно",
    impact: "1000+ решенных вопросов"
  },
];

const services = [
  {
    title: "Разработка проектной документации",
    description: "Полный цикл проектирования светофорных объектов с гарантией качества",
    price: "от 50 000 ₽",
    icon: "📐",
    features: ["3D моделирование", "Техническая экспертиза", "Гарантия 2 года"]
  },
  {
    title: "Аренда автовышек",
    description: "Современные автовышки для обслуживания дорожной инфраструктуры",
    price: "от 15 000 ₽/сутки",
    icon: "📡",
    features: ["Высота до 45м", "Опытные операторы", "Круглосуточно"]
  },
  {
    title: "Вызов эвакуатора",
    description: "Быстрая и бережная эвакуация любого транспорта по городу",
    price: "от 3 000 ₽",
    icon: "🚛",
    features: ["Прибытие за 20 мин", "Любые авто", "Оплата картой"]
  },
];

const news = [
  { 
    title: "Новые правила дорожного движения с 2025 года", 
    date: "01.09.2025",
    excerpt: "Подробный разбор изменений, которые коснутся каждого участника движения",
    category: "Законодательство",
    views: 2340
  },
  { 
    title: "Установлены умные светофоры в центре города", 
    date: "15.08.2025",
    excerpt: "Современная система сокращает время ожидания и улучшает безопасность",
    category: "Технологии",
    views: 1876
  },
  { 
    title: "ЦОДД на городском фестивале безопасности", 
    date: "01.08.2025",
    excerpt: "Интерактивные стенды, викторины и подарки для всех посетителей",
    category: "События",
    views: 945
  },
];

const stats = [
  { number: "200+", label: "Реализованных проектов", icon: CheckCircle },
  { number: "40%", label: "Снижение аварийности", icon: Shield },
  { number: "50000+", label: "Довольных горожан", icon: Heart },
  { number: "24/7", label: "Работаем для вас", icon: Clock },
];

export default function Home() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setCurrentSlide(prev => (prev + 1) % 3);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section with enhanced animations */}
      <section className="relative bg-gradient-to-br from-[#62a744] via-green-600 to-green-800 text-white py-24 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-20 left-10 w-32 h-32 bg-white/5 rounded-full blur-xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-40 h-40 bg-white/5 rounded-full blur-xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/3 w-24 h-24 bg-white/5 rounded-full blur-xl animate-pulse delay-2000"></div>
        </div>
        
        <div className={`max-w-7xl mx-auto text-center relative z-10 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-6 py-2 mb-8 border border-white/20">
            <Star className="w-4 h-4 text-yellow-300" />
            <span className="text-sm font-medium">Работаем с 2010 года • 200+ проектов</span>
          </div>
          <div className="max-w-7xl mx-auto text-center relative z-10">
          {/* Logo */}
         
          <div className="mx-auto mb-12 w-64 h-64 flex items-center       justify-center overflow-hidden">
           <img src={logo} alt="Smolathon Logo" className="transform scale-125" />
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight bg-gradient-to-r from-white to-green-100 bg-clip-text text-transparent">
            ЦОДД Смоленск
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-4xl mx-auto leading-relaxed opacity-90">
            Мы делаем дороги безопаснее, а город удобнее для всех. 
            Каждый день работаем над тем, чтобы вы чувствовали себя защищенными на дорогах Смоленска.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
            <button className="group px-8 py-4 bg-white text-[#62a744] font-bold rounded-xl hover:bg-gray-50 transition-all duration-300 transform hover:scale-105 shadow-2xl flex items-center gap-2 justify-center">
              <Heart className="w-5 h-5 group-hover:text-red-500 transition-colors" />
              Узнать о нас
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="px-8 py-4 bg-transparent border-2 border-white text-white font-bold rounded-xl hover:bg-white/10 backdrop-blur-sm transition-all duration-300 flex items-center gap-2 justify-center">
              <Zap className="w-5 h-5" />
              Наши услуги
            </button>
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div key={index} className="text-center bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20 hover:bg-white/20 transition-all duration-300">
                <stat.icon className="w-8 h-8 mx-auto mb-2 text-green-200" />
                <div className="text-2xl font-bold mb-1">{stat.number}</div>
                <div className="text-sm opacity-90">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
        </div>
      </section>

      {/* Mission Statement Enhanced */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Почему горожане нам доверяют
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Мы не просто контролируем соблюдение правил — мы создаем безопасную и комфортную городскую среду для всех жителей Смоленска
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="group p-8 rounded-2xl bg-gradient-to-br from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 transition-all duration-500 hover:shadow-xl">
              <div className="text-5xl mb-6 group-hover:scale-110 transition-transform duration-300">🛡️</div>
              <h3 className="text-2xl font-bold mb-4 text-gray-900">Безопасность прежде всего</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                За последние 3 года мы снизили количество ДТП в городе на 40% благодаря современным технологиям и грамотному планированию.
              </p>
              <div className="text-sm text-blue-600 font-semibold">
                ✓ Умные светофоры ✓ Безопасные переходы ✓ Контроль скорости
              </div>
            </div>
            
            <div className="group p-8 rounded-2xl bg-gradient-to-br from-green-50 to-green-100 hover:from-green-100 hover:to-green-200 transition-all duration-500 hover:shadow-xl">
              <div className="text-5xl mb-6 group-hover:scale-110 transition-transform duration-300">💚</div>
              <h3 className="text-2xl font-bold mb-4 text-gray-900">Забота о каждом</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Учитываем потребности всех: от родителей с колясками до людей с ограниченными возможностями. Город должен быть удобен для всех.
              </p>
              <div className="text-sm text-green-600 font-semibold">
                ✓ Тактильная плитка ✓ Звуковые сигналы ✓ Широкие тротуары
              </div>
            </div>
            
            <div className="group p-8 rounded-2xl bg-gradient-to-br from-purple-50 to-purple-100 hover:from-purple-100 hover:to-purple-200 transition-all duration-500 hover:shadow-xl">
              <div className="text-5xl mb-6 group-hover:scale-110 transition-transform duration-300">🏙️</div>
              <h3 className="text-2xl font-bold mb-4 text-gray-900">Современные решения</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Используем передовые технологии: ИИ для управления трафиком, мобильные приложения для горожан, экологичные материалы.
              </p>
              <div className="text-sm text-purple-600 font-semibold">
                ✓ Искусственный интеллект ✓ Мобильные приложения ✓ Эко-материалы
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Projects Section Enhanced */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Проекты, которые изменили город
            </h2>
            <p className="text-xl text-gray-600">
              Каждый проект — это конкретная польза для жителей Смоленска
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {projects.map((project, index) => (
              <div 
                key={index}
                className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 overflow-hidden cursor-pointer transform hover:-translate-y-2"
              >
                <div className="p-8">
                  <div className="flex items-center justify-between mb-6">
                    <div className="text-6xl group-hover:scale-110 transition-transform duration-300">
                      {project.icon}
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        project.status === 'Завершено' ? 'bg-green-100 text-green-800' :
                        project.status === 'В процессе' ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {project.status}
                      </span>
                    </div>
                  </div>
                  
                  <h3 className="text-2xl font-bold mb-4 text-gray-900 group-hover:text-[#62a744] transition-colors">
                    {project.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed mb-6">
                    {project.description}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-semibold text-[#62a744]">
                      {project.impact}
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-[#62a744] group-hover:translate-x-1 transition-all" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Section Enhanced */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Профессиональные услуги
            </h2>
            <p className="text-xl text-gray-600">
              Качественные коммерческие услуги от экспертов дорожного хозяйства
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <div 
                key={index}
                className="group border-2 border-gray-100 rounded-2xl p-8 hover:border-[#62a744] hover:shadow-xl transition-all duration-500 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-[#62a744]/10 to-transparent rounded-bl-2xl"></div>
                
                <div className="text-5xl mb-6">{service.icon}</div>
                <h3 className="text-2xl font-bold mb-3 text-gray-900 group-hover:text-[#62a744] transition-colors">
                  {service.title}
                </h3>
                <p className="text-gray-600 mb-6 leading-relaxed">
                  {service.description}
                </p>
                
                <div className="space-y-2 mb-6">
                  {service.features.map((feature, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      {feature}
                    </div>
                  ))}
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-[#62a744]">{service.price}</span>
                  <button className="px-6 py-3 bg-[#62a744] text-white font-semibold rounded-xl hover:bg-green-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
                    Заказать
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section Enhanced */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Команда профессионалов
            </h2>
            <p className="text-xl text-gray-600">
              Опытные специалисты, которые знают свое дело и любят наш город
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {team.map((member, index) => (
              <div 
                key={index}
                className="group bg-white rounded-2xl shadow-lg p-8 text-center hover:shadow-xl transition-all duration-500 transform hover:-translate-y-2"
              >
                <div className="relative mb-6">
                  <div className="w-32 h-32 bg-gradient-to-br from-[#62a744] to-green-600 rounded-full mx-auto flex items-center justify-center text-white text-4xl font-bold shadow-xl group-hover:scale-105 transition-transform duration-300">
                    {member.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center">
                    <Star className="w-4 h-4 text-white" />
                  </div>
                </div>
                
                <h3 className="text-xl font-bold mb-2 text-gray-900">
                  {member.name}
                </h3>
                <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                  {member.role}
                </p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-center gap-2 text-[#62a744] font-semibold">
                    <Clock className="w-4 h-4" />
                    {member.experience}
                  </div>
                  <div className="text-gray-600">
                    {member.achievements}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* News Section Enhanced */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-16">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Последние новости
              </h2>
              <p className="text-xl text-gray-600">
                Будьте в курсе всех изменений и улучшений в городе
              </p>
            </div>
            <button className="flex items-center gap-2 text-[#62a744] font-bold hover:text-green-700 transition-colors group">
              Все новости 
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {news.map((item, index) => (
              <article 
                key={index}
                className="group bg-gray-50 rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-500 cursor-pointer transform hover:-translate-y-2"
              >
                <div className="p-8">
                  <div className="flex items-center justify-between mb-4">
                    <span className="px-3 py-1 bg-[#62a744] text-white text-xs font-semibold rounded-full">
                      {item.category}
                    </span>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Calendar className="w-4 h-4" />
                      {item.date}
                    </div>
                  </div>
                  
                  <h3 className="text-xl font-bold mb-4 text-gray-900 group-hover:text-[#62a744] transition-colors leading-tight">
                    {item.title}
                  </h3>
                  <p className="text-gray-600 mb-4 leading-relaxed">
                    {item.excerpt}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Users className="w-4 h-4" />
                      {item.views} просмотров
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-[#62a744] group-hover:translate-x-1 transition-all" />
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Contact CTA Section Enhanced */}
      <section className="py-20 px-4 bg-gradient-to-br from-[#62a744] via-green-600 to-green-800 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="absolute top-0 left-0 w-full h-full opacity-10">
          <div className="absolute top-10 left-10 w-32 h-32 border border-white rounded-full"></div>
          <div className="absolute bottom-10 right-10 w-40 h-40 border border-white rounded-full"></div>
          <div className="absolute top-1/2 left-1/3 w-24 h-24 border border-white rounded-full"></div>
        </div>
        
        <div className="max-w-6xl mx-auto text-center relative z-10">
          <h2 className="text-4xl font-bold mb-6">
            Остались вопросы? Мы всегда на связи!
          </h2>
          <p className="text-xl mb-12 opacity-90 max-w-3xl mx-auto">
            Наша команда готова помочь вам 24/7. Свяжитесь с нами любым удобным способом — мы ответим быстро и подробно.
          </p>
          
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <Phone className="w-8 h-8 mx-auto mb-4 text-green-200" />
              <div className="font-bold mb-2">Телефон</div>
              <div className="text-sm opacity-90">+7 (4812) 123-456</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <Mail className="w-8 h-8 mx-auto mb-4 text-green-200" />
              <div className="font-bold mb-2">Email</div>
              <div className="text-sm opacity-90">info@codd-smolensk.ru</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <MapPin className="w-8 h-8 mx-auto mb-4 text-green-200" />
              <div className="font-bold mb-2">Офис</div>
              <div className="text-sm opacity-90">ул. Ленина, 1, Смоленск</div>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <button className="group px-8 py-4 bg-white text-[#62a744] font-bold rounded-xl hover:bg-gray-50 transition-all duration-300 transform hover:scale-105 shadow-2xl flex items-center gap-2 justify-center">
              <Phone className="w-5 h-5" />
              Позвонить нам
            </button>
            <button className="px-8 py-4 bg-transparent border-2 border-white text-white font-bold rounded-xl hover:bg-white/10 backdrop-blur-sm transition-all duration-300 flex items-center gap-2 justify-center">
              <Mail className="w-5 h-5" />
              Написать письмо
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}