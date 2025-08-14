from django.core.management.base import BaseCommand
from services.models import Service, ServiceFeature

class Command(BaseCommand):
    help = 'Add sample services to the database'

    def handle(self, *args, **options):
        # Create service features
        features = {
            'web_dev': [
                'Custom Website Development',
                'Responsive Design',
                'SEO Optimization',
                'Content Management System',
                'Database Design',
                'API Integration',
                'E-commerce Solutions',
                'Performance Optimization'
            ],
            'mobile_dev': [
                'Cross-platform Development',
                'Native iOS Development',
                'Native Android Development',
                'App Store Optimization',
                'Push Notifications',
                'Offline Functionality',
                'Biometric Authentication',
                'Real-time Sync'
            ],
            'ui_ux': [
                'User Research',
                'Wireframing & Prototyping',
                'Visual Design',
                'User Testing',
                'Design Systems',
                'Accessibility Design',
                'Interactive Prototypes',
                'Design Documentation'
            ],
            'seo': [
                'Keyword Research',
                'On-page SEO',
                'Technical SEO',
                'Content Strategy',
                'Link Building',
                'Local SEO',
                'Analytics Setup',
                'Performance Monitoring'
            ],
            'consultation': [
                'Project Planning',
                'Technology Stack Selection',
                'Architecture Design',
                'Code Review',
                'Performance Audit',
                'Security Assessment',
                'Scalability Planning',
                'Best Practices Guidance'
            ]
        }

        # Create features
        created_features = {}
        for category, feature_list in features.items():
            created_features[category] = []
            for feature_name in feature_list:
                feature, created = ServiceFeature.objects.get_or_create(
                    name=feature_name,
                    defaults={'description': f'Professional {feature_name.lower()} service'}
                )
                created_features[category].append(feature)
                if created:
                    self.stdout.write(f'Created feature: {feature_name}')

        # Sample services data
        services_data = [
            {
                'title': 'Full Stack Web Development',
                'description': 'Complete web application development from frontend to backend, including database design and deployment.',
                'category': 'web',
                'price': 75.00,
                'price_type': 'hourly',
                'icon': 'fas fa-code',
                'duration': '2-8 weeks',
                'team_size': '1-3 developers',
                'delivery_time': 'Flexible',
                'additional_info': 'Includes hosting setup, SSL certificate, and 3 months of support.',
                'is_popular': True,
                'order': 1,
                'features': created_features['web_dev']
            },
            {
                'title': 'Mobile App Development',
                'description': 'Native and cross-platform mobile applications for iOS and Android with modern frameworks.',
                'category': 'mobile',
                'price': 85.00,
                'price_type': 'hourly',
                'icon': 'fas fa-mobile-alt',
                'duration': '4-12 weeks',
                'team_size': '1-2 developers',
                'delivery_time': 'Flexible',
                'additional_info': 'Includes app store submission, testing, and 6 months of support.',
                'is_popular': True,
                'order': 2,
                'features': created_features['mobile_dev']
            },
            {
                'title': 'UI/UX Design',
                'description': 'Professional user interface and user experience design with modern design principles.',
                'category': 'design',
                'price': 65.00,
                'price_type': 'hourly',
                'icon': 'fas fa-palette',
                'duration': '1-4 weeks',
                'team_size': '1 designer',
                'delivery_time': 'Flexible',
                'additional_info': 'Includes design system, prototypes, and design handoff.',
                'is_popular': True,
                'order': 3,
                'features': created_features['ui_ux']
            },
            {
                'title': 'SEO Optimization',
                'description': 'Comprehensive search engine optimization to improve your website\'s visibility and ranking.',
                'category': 'seo',
                'price': 45.00,
                'price_type': 'hourly',
                'icon': 'fas fa-search',
                'duration': 'Ongoing',
                'team_size': '1 specialist',
                'delivery_time': 'Monthly reports',
                'additional_info': 'Includes monthly reports, keyword tracking, and performance analysis.',
                'is_popular': False,
                'order': 4,
                'features': created_features['seo']
            },
            {
                'title': 'Technical Consultation',
                'description': 'Expert technical consultation for project planning, architecture, and technology decisions.',
                'category': 'consultation',
                'price': 95.00,
                'price_type': 'hourly',
                'icon': 'fas fa-lightbulb',
                'duration': 'As needed',
                'team_size': '1 consultant',
                'delivery_time': 'Flexible',
                'additional_info': 'Includes detailed reports, recommendations, and follow-up support.',
                'is_popular': False,
                'order': 5,
                'features': created_features['consultation']
            },
            {
                'title': 'E-commerce Development',
                'description': 'Complete e-commerce solutions with payment integration, inventory management, and admin dashboard.',
                'category': 'web',
                'price': 90.00,
                'price_type': 'hourly',
                'icon': 'fas fa-shopping-cart',
                'duration': '6-12 weeks',
                'team_size': '2-4 developers',
                'delivery_time': 'Flexible',
                'additional_info': 'Includes payment gateway setup, SSL certificate, and 6 months of support.',
                'is_popular': True,
                'order': 6,
                'features': created_features['web_dev']
            },
            {
                'title': 'API Development',
                'description': 'RESTful and GraphQL API development with comprehensive documentation and testing.',
                'category': 'web',
                'price': 70.00,
                'price_type': 'hourly',
                'icon': 'fas fa-server',
                'duration': '2-6 weeks',
                'team_size': '1-2 developers',
                'delivery_time': 'Flexible',
                'additional_info': 'Includes API documentation, testing suite, and deployment setup.',
                'is_popular': False,
                'order': 7,
                'features': created_features['web_dev']
            },
            {
                'title': 'WordPress Development',
                'description': 'Custom WordPress themes, plugins, and website development with modern standards.',
                'category': 'web',
                'price': 55.00,
                'price_type': 'hourly',
                'icon': 'fab fa-wordpress',
                'duration': '1-4 weeks',
                'team_size': '1 developer',
                'delivery_time': 'Flexible',
                'additional_info': 'Includes theme customization, plugin development, and content migration.',
                'is_popular': False,
                'order': 8,
                'features': created_features['web_dev']
            }
        ]

        # Create services
        for service_data in services_data:
            features = service_data.pop('features')
            service, created = Service.objects.get_or_create(
                title=service_data['title'],
                defaults=service_data
            )
            if created:
                service.features.set(features)
                self.stdout.write(
                    self.style.SUCCESS(f'Created service: {service.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Service already exists: {service.title}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully added sample services!')
        ) 