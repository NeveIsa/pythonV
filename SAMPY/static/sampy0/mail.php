<?php

$to = "smpdmohanty@gmail.com";

$subject = "isasense.tk visitor's message from : " . $_POST['name'] . " with email id : " . $_POST['email'];
$message = $_POST["message"];
if(mail ( $to , $subject , $message))
{
 echo "Mail Sent Successfully...";
}
else
{
 echo "failed to send mail...";
}


?>

<a href="/">BACK</a>

