
# Инструмент отладки обмена заказами "1С-Битрикс: Управление сайтом" (редакция Интернет-магазин) и "1С: Управление торговлей"

## Получение заказов из 1С-Битрикс

`python3 getorders.py <server_address> <username> <password> <version>`

Для version рекомендуется использовать значение 3.1

Код для запуска в битриксе (если необходимо):

    // Установить последнее время запроса списка заказов
    $newtime = strtotime('10.07.2023 00:00:00');
    \Bitrix\Main\Config\Option::set("sale", "last_export_time_committed_/bitrix/admin/1c_excha", $newtime);

    // Посмотреть последнее время запроса списка заказов
    $time =  \Bitrix\Main\Config\Option::get("sale", "last_export_time_committed_/bitrix/admin/1c_excha", "0");
    echo date('d.m.Y H:i:s', $time);
