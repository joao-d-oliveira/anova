import { notifications, NotificationData} from "@mantine/notifications";

const notificationErrorParameters = {
    color: 'red',
    position: 'top-right',
} as NotificationData;

const notificationSuccessParameters = {
    color: 'green',
    position: 'top-right',
} as NotificationData;

export function errorNotification(message: string) {
    notifications.show({
        ...notificationErrorParameters,
        message,
    });
}

export function successNotification(message: string) {
    notifications.show({
        ...notificationSuccessParameters,
        message,
    });
}