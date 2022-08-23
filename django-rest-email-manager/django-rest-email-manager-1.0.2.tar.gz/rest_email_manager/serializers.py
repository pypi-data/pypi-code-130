from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import EmailAddress


User = get_user_model()


class EmailAddressSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = EmailAddress
        fields = ["email", "current_password"]

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists"
            )

        return email

    def validate_current_password(self, password):
        if self.context["request"].user.check_password(password):
            return password
        else:
            raise serializers.ValidationError("Invalid password")

    def create(self, validated_data):
        validated_data.pop("current_password")

        try:
            return self.context["request"].user.emailaddresses.get(
                email=validated_data["email"]
            )
        except EmailAddress.DoesNotExist:
            return super().create(validated_data)


class EmailAddressKeySerializer(serializers.Serializer):
    key = serializers.CharField()

    def validate_key(self, key):
        try:
            self.emailaddress = EmailAddress.objects.get(
                key=key, user=self.context["request"].user
            )

            if User.objects.filter(email=self.emailaddress.email).exists():
                raise serializers.ValidationError(
                    "Email address is already in use"
                )

            if self.emailaddress.is_expired:
                raise serializers.ValidationError(
                    "Verification key has expired"
                )
        except EmailAddress.DoesNotExist:
            raise serializers.ValidationError("Invalid verification key")

    def save(self):
        self.emailaddress.verify()
