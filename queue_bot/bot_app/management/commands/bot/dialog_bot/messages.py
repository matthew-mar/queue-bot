class DialogStartMessages:
    MESSAGE = "функции бота"


class QueueCreateMessages:
    NOT_OWNER_MESSAGE = (
        "чтобы создавать очереди нужно быть владельцем беседы, "
        "где есть бот"
    )
    
    MEMBER_NOT_SAVED_MESSAGE = (
        "чтобы пользоваться функциями бота нужно состоять в одной "
        "беседе с ботом"
    )

    CHOOSE_CHAT_MESSAGE = "выберите беседу, в которой будет очередь"

    QUEUE_NAME_ENTER_MESSAGE = "введите название очереди"

    OWNER_ERROR_MESSAGE = "ошибка! вы не являетесь владельцем этой беседы"

    DAY_ENTER_MESSAGE = "введите день недели, когда начнет работать очередь"

    TIME_ENTER_MESSAGE = (
        "укажите время, когда начнет работать очередь\n"
        "формат ввода: hh:mm"
    )

    DAY_ERROR_MESSAGE = "ошибка! введите правильно день недели"

    MEMBERS_ADD_MESSAGE = (
        "Добавить участников беседы в очередь?\n"
        "Да - участники беседы добавятся автоматически по порядку\n"
        "Нет - участники беседы будут сами записываться в произвольном порядке"
    )

    TIME_FORMAT_ERROR = "ошибка! неверный формат данных"

    QUEUE_ALREADY_SAVED_MESSAGE = "ошибка! такая очередь уже существует."

    QUEUE_SUCCESSFULLY_SAVED_MESSAGE = "очередь успешно сохранена"

    YES_NO_ERROR_MESSAGE = "ответьте да или нет"


class QueueEnrollMessages:
    NO_QUEUES_MESSAGE = "для вас нет очередей"

    CHOOSE_QUEUE_MESSAGE = "выберите очередь, в которую хотите записаться"

    ALREADY_IN_QUEUE_MESSAGE =(
        "вы уже находитесь в этой очереди\n"
        "ваш текущий порядковый номер - {0}"
    )

    QUEUE_ENROLLED_MESSAGE = (
        "вы записались в очередь {0} из беседы {1}\n"
        "ваш текущий номер - {2}"
    )

    QUEUE_ENROLL_ERROR_MESSAGE = "ошибка! выберите очередь из представленного списка"


class QueueQuitMessages:
    NOT_IN_ANY_QUEUE_MESSAGE = "вы не состоите ни в одной очереди"

    CHOOSE_QUEUE_MESSAGE = "выберите очередь, из которой хотите удалиться"

    ON_QUIT_MESSAGE = "вы удалились из очереди {0} в беседе {1}"

    QUEUE_ERROR_MESSAGE = "ошибка! выберите очередь из предложенного списка"


class GetQueuePlaceMessages:
    CHOOSE_QUEUE_MESSAGE = "выберите очередь"

    QUEUE_ORDER_MESSAGE = "ваш номер в очереди - {0}\n{1}"


class ChatInvitationMessages:
    START_MESSAGE = (
        "чтобы пользоваться моими функциями сделайте меня администратором "
        "и нажмите кнопку \"start\""
    )


class ChatStartMessages:
    CHAT_SAVED_MESSAGE = (
        "ваша беседа успешно сохранена, теперь вы можете "
        "создавать очереди"
    )

    NOT_ADMIN_ERROR_MESSAGE = "сделайте бота администратором и повторите попытку"


class NewQueueSignalMessages:
    NEW_QUEUE_MESSAGE = (
        "в вашей беседе появилась очередь {queue_name}\n"
        "очередь начнет работать {queue_datetime} в {queue_start_time}\n"
    )

    MEMBERS_SAVED_MESSAGE = (
        "все пользователи добавлены в очередь\n"
        "во время начала очереди вам будут приходить уведомления о "
        "вашей позиции в очеред\n"
        "текущий порядок очереди:\n\n"
        "{0}"
    )

    START_ENROLL_MESSAGE = "вы можете начать записываться в очередь"
