import pytesseract
from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document
from .serializers import DocumentSerializer


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

                # Save the extracted text to the Document model
                document.extracted_text = extracted_text
                document.save()

                return Response({
                    "message": "File uploaded and processed successfully",
                    "extracted_text": extracted_text
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": f"OCR processing error: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # Log and handle any unexpected errors
            print(f"Unexpected error: {str(e)}")  # Logs error to the console
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProofOfAddressView(APIView):
    def post(self, request):
        # Initial business logic for Proof of Address can go here
        return Response({"message": "Processing Proof of Address"}, status=status.HTTP_200_OK)
