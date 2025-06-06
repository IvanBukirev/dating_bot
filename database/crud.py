from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databasework import engine, session
from models import Users, Candidates, Photos, Interactions, UsersCandidates


def add_user(session, vk_id, name, age, gender, city):
    try:
        # Проверяем, существует ли уже пользователь с таким vk_id
        existing_user = session.query(Users).filter_by(vk_id=vk_id).first()
        if existing_user:
            # print(f"Пользователь с VK ID {vk_id} уже существует")
            return existing_user

        new_user = Users(
            vk_id=vk_id,
            name=name,
            age=age,
            gender=gender,
            city=city
        )

        session.add(new_user)
        session.commit()
        # print(f"Пользователь {name} успешно добавлен")
        return new_user

    except Exception as e:
        session.rollback()
        # print(f"Ошибка при добавлении пользователя: {e}")
        raise


def add_candidate_with_link(session, user_vk_id, candidate_vk_id, name, age, gender, city, photos_data):
    try:
        # Находим пользователя
        user = session.query(Users).filter_by(vk_id=user_vk_id).first()
        if not user:
            raise ValueError(f"Пользователь с VK ID {user_vk_id} не найден")

        # Проверяем, существует ли уже кандидат с таким vk_id
        existing_candidate = session.query(Candidates).filter_by(vk_id=candidate_vk_id).first()

        if existing_candidate:
            # Если кандидат уже существует, проверяем связь с пользователем
            existing_link = session.query(UsersCandidates).filter_by(
                user_id=user.id,
                candidate_id=existing_candidate.id
            ).first()

            if existing_link:
                # print(f"Кандидат {name} уже связан с пользователем {user.name}")
                return existing_candidate, existing_link
        else:
            # Создаем нового кандидата
            new_candidate = Candidates(
                vk_id=candidate_vk_id,
                name=name,
                age=age,
                gender=gender,
                city=city
            )
            session.add(new_candidate)
            session.flush()  # Получаем ID нового кандидата

            # Добавляем фото кандидата
            new_photos = Photos(
                candidate_id=new_candidate.id,
                first_photo=photos_data['first_photo'],
                second_photo=photos_data['second_photo'],
                third_photo=photos_data['third_photo'],
                account_link=photos_data['account_link']
            )
            session.add(new_photos)

            existing_candidate = new_candidate

        # Создаем связь между пользователем и кандидатом
        new_link = UsersCandidates(
            user_id=user.id,
            candidate_id=existing_candidate.id
        )
        session.add(new_link)
        session.commit()

        # print(f"Кандидат {name} успешно добавлен и связан с пользователем {user.name}")
        return existing_candidate, new_link

    except Exception as e:
        session.rollback()
        # print(f"Ошибка при добавлении кандидата: {e}")
        raise


def add_interaction(session, user_vk_id, candidate_vk_id, status):
    try:
        # Находим пользователя и кандидата
        user = session.query(Users).filter_by(vk_id=user_vk_id).first()
        if not user:
            raise ValueError(f"Пользователь с VK ID {user_vk_id} не найден")

        candidate = session.query(Candidates).filter_by(vk_id=candidate_vk_id).first()
        if not candidate:
            raise ValueError(f"Кандидат с VK ID {candidate_vk_id} не найден")

        # Проверяем, существует ли уже такое взаимодействие
        existing_interaction = session.query(Interactions).filter_by(
            user_id=user.id,
            candidate_id=candidate.id
        ).first()

        if existing_interaction:
            # print(f"Взаимодействие между пользователем {user.name} и кандидатом {candidate.name} уже существует")
            return existing_interaction

        # Создаем новое взаимодействие
        new_interaction = Interactions(
            user_id=user.id,
            candidate_id=candidate.id,
            status=status
        )

        session.add(new_interaction)
        session.commit()

        # print(f"Создано взаимодействие между пользователем {user.name} и кандидатом {candidate.name} со статусом '{status}'")
        return new_interaction

    except Exception as e:
        session.rollback()
        # print(f"Ошибка при создании взаимодействия: {e}")
        raise


def get_user_interactions_with_candidates(session, user_vk_id):

    try:
        # Находим пользователя
        user = session.query(Users).filter_by(vk_id=user_vk_id).first()
        if not user:
            raise ValueError(f"Пользователь с VK ID {user_vk_id} не найден")

        # Получаем все взаимодействия пользователя с информацией о кандидатах
        interactions = session.query(Interactions, Candidates). \
            join(Candidates, Interactions.candidate_id == Candidates.id). \
            filter(Interactions.user_id == user.id). \
            all()

        result = []
        for interaction, candidate in interactions:
            result.append({
                'candidate_id': candidate.id,
                'candidate_vk_id': candidate.vk_id,
                'candidate_name': candidate.name,
                'candidate_age': candidate.age,
                'candidate_gender': candidate.gender,
                'candidate_city': candidate.city,
                'interaction_id': interaction.id,
                'interaction_status': interaction.status,
                'interaction_date': interaction.created_at if hasattr(interaction, 'created_at') else None
            })

        return result

    except Exception as e:
        # print(f"Ошибка при получении взаимодействий пользователя: {e}")
        raise


# # Для тестирования
# if __name__ == "__main__":
#
#     try:
#         # # Создаем таблицы (если их нет)
#         # Base.metadata.create_all(engine)
#
#         # Добавляем пользователя
#         user = add_user(
#             session=session,
#             vk_id=123456789,
#             name="Иван Тест",
#             age=30,
#             gender="male",
#             city="Москва"
#         )
#
#         # Добавляем кандидата и связываем с пользователем
#         candidate, link = add_candidate_with_link(
#             session=session,
#             user_vk_id=123456789,
#             candidate_vk_id=987654321,
#             name="Мария Тест0",
#             age=28,
#             gender="female",
#             city="Москва",
#             photos_data={
#                 'first_photo': 'photo1.jpg',
#                 'second_photo': 'photo2.jpg',
#                 'third_photo': 'photo3.jpg',
#                 'account_link': 'https://vk.com/id987654321'
#             }
#         )
#
#     finally:
#         session.close()