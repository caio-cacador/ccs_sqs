from datetime import datetime
import ujson
import boto3


class Message:

    def __init__(self, sqs_message: dict):
        self.sqs_message = sqs_message

    @property
    def body(self):
        return ujson.loads(self.sqs_message.get('Body', ''))

    @property
    def sent_timestamp(self):
        timestamp = self.sqs_message.get('Attributes', {}).get('SentTimestamp')
        return int(timestamp) if timestamp else None

    @property
    def message_id(self):
        return self.sqs_message.get('MessageId', '')

    @property
    def receipt_handle(self):
        return self.sqs_message.get('ReceiptHandle', '')

    @property
    def message_author(self):
        return self.sqs_message.get('MessageAttributes', {}).get('Author', {}).get('StringValue', '')


class SQS:

    def __init__(self, queue_url: str, application_name: str, aws_region: str):
        self._sqs = boto3.client('sqs', region_name=aws_region)
        self._application_name = application_name
        self._queue_url = queue_url

    def send_message(self, message: dict):
        timestamp = datetime.utcnow().timestamp()
        response = self._sqs.send_message(
            QueueUrl=self._queue_url,
            MessageGroupId=self._application_name,
            MessageAttributes={
                'Author': {
                    'DataType': 'String',
                    'StringValue': self._application_name
                },
                'SentTimestamp': {
                    'DataType': 'Number',
                    'StringValue': str(timestamp)
                }
            },
            MessageBody=ujson.dumps(message)
        )
        return response

    def get_message(self, max_number_of_messages: int = 1, visibility_timeout: int = 20, delete_message: bool = False,
                    wait_time: int = 20):
        response = self._sqs.receive_message(
            QueueUrl=self._queue_url,
            AttributeNames=['SentTimestamp', 'Author'],
            MaxNumberOfMessages=max_number_of_messages,
            MessageAttributeNames=['All'],
            VisibilityTimeout=visibility_timeout,
            WaitTimeSeconds=wait_time
        )

        if response.get('Messages'):
            for message in response['Messages']:
                if delete_message:
                    self.delete_message(message['ReceiptHandle'])
            results = [Message(msg) for msg in response['Messages']]
            return results[0] if max_number_of_messages == 1 else results
        return None

    def delete_message(self, receipt_handle):
        return self._sqs.delete_message(QueueUrl=self._queue_url, ReceiptHandle=receipt_handle)
