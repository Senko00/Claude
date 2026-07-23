<?php
/**
 * Загрузите этот файл на сайт simkran.ru (в корень сайта или в любую папку)
 * и укажите его URL в .env как BITRIX_ENDPOINT_URL.
 *
 * Обходит REST API (на этой инсталляции нет методов iblock.*) и создаёт
 * новость напрямую через внутреннее API Bitrix (CIBlockElement::Add),
 * с тем же эффектом, что и добавление новости из админки — кэш и поиск
 * обновятся штатно.
 *
 * ВАЖНО: замените SECRET ниже на длинную случайную строку (например,
 * результат `python -c "import secrets; print(secrets.token_hex(32))"`)
 * и ту же строку впишите в .env как BITRIX_ENDPOINT_SECRET. Любой, кто
 * узнает URL и секрет, сможет создавать новости на сайте.
 */

header('Content-Type: application/json; charset=utf-8');

define("NO_KEEP_STATISTIC", true);
require($_SERVER["DOCUMENT_ROOT"] . "/bitrix/modules/main/include/prolog_before.php");

const SECRET = "ЗАМЕНИТЕ_НА_СВОЙ_СЛУЧАЙНЫЙ_КЛЮЧ";

$input = json_decode(file_get_contents("php://input"), true);

if (!is_array($input) || !isset($input["secret"]) || !hash_equals(SECRET, (string)$input["secret"])) {
    http_response_code(403);
    echo json_encode(["error" => "forbidden"]);
    exit;
}

$iblockId = (int)($input["iblock_id"] ?? 0);
$title = (string)($input["title"] ?? "");
$text = (string)($input["text"] ?? "");
$imageB64 = (string)($input["image_base64"] ?? "");

if (!$iblockId || $title === "" || $text === "") {
    http_response_code(400);
    echo json_encode(["error" => "iblock_id, title, text обязательны"]);
    exit;
}

$code = CUtil::translit($title, "ru", [
    "max_len" => 100,
    "change_case" => "L",
    "replace_space" => "-",
    "replace_other" => "-",
    "delete_repeat_replace" => true,
]);
$code = trim($code, "-") . "-" . substr(md5(uniqid("", true)), 0, 6);

$fields = [
    "IBLOCK_ID" => $iblockId,
    "NAME" => $title,
    "CODE" => $code,
    "ACTIVE" => "Y",
    "PREVIEW_TEXT" => mb_substr($text, 0, 255),
    "DETAIL_TEXT" => $text,
    "DETAIL_TEXT_TYPE" => "text",
];

$tmpFile = null;
if ($imageB64 !== "") {
    $tmpFile = tempnam(sys_get_temp_dir(), "news_") . ".jpg";
    file_put_contents($tmpFile, base64_decode($imageB64));
    $picture = CFile::MakeFileArray($tmpFile, "image/jpeg");
    $fields["PREVIEW_PICTURE"] = $picture;
    $fields["DETAIL_PICTURE"] = $picture;
}

$el = new CIBlockElement;
$id = $el->Add($fields);

if ($tmpFile && file_exists($tmpFile)) {
    unlink($tmpFile);
}

if ($id) {
    $url = null;
    $ibProps = CIBlock::GetArrayByID($iblockId);
    if ($ibProps && !empty($ibProps["DETAIL_PAGE_URL"])) {
        $path = CIBlockElement::GetIBlockElementURL($iblockId, $id, $ibProps["DETAIL_PAGE_URL"]);
        $url = "https://simkran.ru" . $path;
    }
    echo json_encode(["result" => ["ID" => $id, "URL" => $url]]);
} else {
    http_response_code(500);
    echo json_encode(["error" => $el->LAST_ERROR]);
}
