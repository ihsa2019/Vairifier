import re
import json
from datetime import datetime
import pytesseract
from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document, PersonalInformation
from .serializers import DocumentSerializer
from django.shortcuts import get_object_or_404

class HomeView(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the landing screen"}, status=status.HTTP_200_OK)


class ApiRootView(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the API root endpoint"})


class DocumentUploadView(APIView):
    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({"message": "Document upload endpoint"}, status=status.HTTP_200_OK)


class ProofOfIdentityView(APIView):
    def post(self, request):
        try:
            # Check if a file is present in the request
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            # Set a default user_id if not provided
            user_id = request.data.get('user_id', 1)  # Replace with appropriate logic for your app

            # Save the file and create a Document record
            document = Document.objects.create(
                document_file=uploaded_file,
                document_type='passport',
                user_id=user_id
            )

            # Process the uploaded file with OCR
            try:
                image = Image.open(uploaded_file)
                extracted_text = pytesseract.image_to_string(image)

                # Parse the extracted text
                parsed_data = self.parse_ocr_text(extracted_text)

                # Save the extracted text to the Document model
                document.extracted_text = extracted_text
                document.save()

                # Compare with database data
                comparison_result = self.compare_with_database(parsed_data)

                return Response({
                    "message": "File uploaded and processed successfully",
                    "extracted_text": extracted_text,
                    # "splitted_text": parsed_data
                    "comparison_result": comparison_result
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": f"OCR processing error: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # Log and handle any unexpected errors
            print(f"Unexpected error: {str(e)}")  # Logs error to the console
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def parse_ocr_text(self, ocr_text):
        # Remove multiple line breaks and replace them with a single space
        extracted_text = re.sub(r"\n+", " ", ocr_text).strip()

        # Define regex patterns for each field
        patterns = {
            "first_name": r"First Name\s+([A-Za-z]+)",
            "last_name": r"Last Name\s+([A-Za-z]+)"
        }

        # Extract information using regex patterns
        data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, extracted_text)
            data[key] = match.group(1).strip() if match else None

        # Add full_name by concatenating first_name and last_name if both are present
        if data["first_name"] and data["last_name"]:
            data["full_name"] = f"{data['first_name']} {data['last_name']}"
        else:
            data["full_name"] = None

        return data

    @staticmethod
    def compare_with_database(parsed_data):
        # Query the PersonalInformation table based on full name
        try:
            user_profile = get_object_or_404(PersonalInformation, full_name=parsed_data["full_name"])

            # Compare fields from parsed_data with UserProfile fields
            mismatches = {}
            for field, value in parsed_data.items():
                db_value = getattr(user_profile, field, None)
                if db_value != value:
                    mismatches[field] = {"db_value": db_value, "extracted_value": value}

            if not mismatches:
                return {"message": "All fields match the database record."}
            else:
                return {"message": "Some fields do not match", "mismatches": mismatches}

        except PersonalInformation.DoesNotExist:
            return {"message": "No matching user profile found in the database."}


class ProofOfAddressView(APIView):
    def post(self, request):
        # Initial business logic for Proof of Address can go here
        return Response({"message": "Processing Proof of Address"}, status=status.HTTP_200_OK)
