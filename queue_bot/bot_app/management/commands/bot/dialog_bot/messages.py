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
