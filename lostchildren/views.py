import json
import numpy as np
import re
from django.db.models import Q, Count, OuterRef
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from findmychild.custom_methods import IsAuthenticatedCustom, PermissionRequiredCustom
from rest_framework.response import Response
from .models import LostChild, FoundChild, MatchingChild, ReceivedChild, Report, Status
from .serializers import ReportSerializer, MatchingChildSerializer
from .face_recognizer import feature_extractor, match_results
from django.forms.models import model_to_dict
from login_app.models import User, Role
from notification_app.models import MatchNotification, DropChildNotification
from notification_app.serializers import MatchNotificationSerializer, DropChildNotificationSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import threading
from .signals import delete_child_image

def sendMatchingNotificaitons(child, founder):
    channel_layer = get_channel_layer()
    try:
        queryset = LostChild.objects.all()
    except LostChild.DoesNotExist:
        return Response({'error': 'No Lost Reports Found to Match with'}, status=404)
    # get image encoding of the child
    image_encoding = np.array(json.loads(child.image_encoding))
    # iterate through all reports and check for matching faces
    # matched_reports = []
    # distances = []
    for report in queryset:
        if report.image_encoding is not None:
            report_encoding = np.array(json.loads(report.image_encoding))
        else:
            report_encoding = None
        print(report.child_name)
        if child.gender == report.gender:
            is_matched, distance = match_results(
                image_encoding, report_encoding)
            if report_encoding is not None and np.all(is_matched):
                # matched_reports.append(report)
                # distances.append(distance)
                matching_child_obj = MatchingChild.objects.create(recieved_child = child, lost_child = report,
                distance= distance)
                try:
                    # report.matchingReports.reports.add(
                    #     matching_child_obj)
                    notification = MatchNotification.objects.create(user_id=report.reporter.id,
                                                                    lost_child=report,
                                                                    matching_child_id=matching_child_obj.id, description="Match Report")
                    serialized_notification = MatchNotificationSerializer(
                        notification).data
                    print(serialized_notification)
                    async_to_sync(channel_layer.group_send)(
                        f"{report.reporter_id}",
                        {
                            "type": "match_found",
                            "message": serialized_notification,
                        },
                    )
                except Exception as e:
                    print(e)
    try:
        drop_notification = DropChildNotification.objects.create(type= "drop_child_success", description="Child is Received Successfully",user = founder, found_child = child  )
        serialized_drop_notification = DropChildNotificationSerializer(drop_notification).data
        async_to_sync(channel_layer.group_send)(
                            f"{founder.id}",
                            {
                                "type": "drop_child_success",
                                "message": serialized_drop_notification,
                            },
                        )
    except Exception as e:
        return Exception(e)
    
    onlineAppUsers = User.objects.filter(role=Role.APPUSER, online_status=True)
    for user in onlineAppUsers:
        try:
            async_to_sync(channel_layer.group_send)(
                            f"{user.id}",
                            {
                                "type": "new_received_child",
                                "message": ReportSerializer(child).data,
                            },
                        )
        except Exception as e:
            print(e)
    # serializer = ReportSerializer(matched_reports, many=True)
    # output_data = []
    # for i, data in enumerate(serializer.data):
    #     output_data.append({
    #         'Child': OrderedDict(data.items()),
    #         'distance': {'distance': distances[i]}
    #     })

def createMatches(child):
    # child.generate_face_encodings()
    # child.save()
    print("called")
    queryset = ReceivedChild.objects.all()
    if not queryset.exists():
        # try:
        #     matchingReports_obj = child.matchingReports
        # except Exception:
        #     matchingReports_obj = MatchingReports.objects.create(
        #         lost_child=child)
        print('No Received Reports Found to Match with')
        return {'error': 'No Received Reports Found to Match with'}
    # get image encoding of the child
    image_encoding = np.array(json.loads(child.image_encoding))
    # iterate through all reports and check for matching faces
    for report in queryset:
        if report.image_encoding is not None:
            report_encoding = np.array(json.loads(report.image_encoding))
        else:
            report_encoding = None
        print(report.child_name)
        if child.gender == report.gender:
            is_matched, distance = match_results(
                image_encoding, report_encoding)
            if report_encoding is not None and np.all(is_matched):
                # try:
                #     matchingReports_obj.reports.get(
                #         recieved_child_id=report.id)
                # except Exception:
                #     match_obj = {
                #         "recieved_child": model_to_dict(report),
                #         "distance": distance
                #     }
                #     serialized_report = MatchingChildSerializer(
                #         data=match_obj)
                #     if serialized_report.is_valid(raise_exception=True):
                #         matching_child_obj = serialized_report.save(
                #             recieved_child=report)
                #         matchingReports_obj.reports.add(matching_child_obj)
                try:
                    MatchingChild.objects.get(recieved_child = report, lost_child = child)
                except:
                    MatchingChild.objects.create(recieved_child = report, lost_child = child,
                    distance= distance)
    matching_children = MatchingChild.objects.filter(lost_child = child)
    matched_reports = MatchingChildSerializer(matching_children, many=True)
    
    return matched_reports.data
    # return Response(matched_reports.data, status=status.HTTP_200_OK)
    # print(model_to_dict(matchingReports_obj))
    # return MatchingReportsSerializer(matchingReports_obj).data
        
class LostChildren(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticatedCustom, )

    queryset = LostChild.objects.all()
    serializer_class = ReportSerializer


class FoundChildren(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticatedCustom, )

    queryset = FoundChild.objects.all()
    serializer_class = ReportSerializer

class LostChildList(PermissionRequiredCustom, generics.ListAPIView):
     
    queryset = LostChild.objects.all()
    serializer_class = ReportSerializer
    permission_required = 'lostchildren.view_lostchild'


class FoundChildList(PermissionRequiredCustom, generics.ListAPIView):

    permission_required = 'lostchildren.view_foundchild'

    queryset = FoundChild.objects.all()
    serializer_class = ReportSerializer

class ReceivedChildList(PermissionRequiredCustom, generics.ListAPIView):

    permission_required = 'lostchildren.view_receivedchild'

    queryset = ReceivedChild.objects.all()
    serializer_class = ReportSerializer


class LostChildCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticatedCustom, )
    serializer_class = ReportSerializer

    def post(self, request, format=None):
        request.data['reporter'] = request.user.id
        reportData = request.data
        print(reportData)
        # reportData.pop("date")
        # reportData["reporter"] = request.user.id
        serializer = self.serializer_class(data=reportData)
        serializer.is_valid(raise_exception=True)
        child = serializer.save()
        # child.generate_face_encodings()
        # child.save()
        # print(child)
        # try:
        #     # queryset = FoundChild.objects.all()
        #     queryset = FoundChild.objects.filter(status='received')
        #     try:
        #         matchingReports_obj = child.matchingReports
        #     except Exception:
        #         matchingReports_obj = MatchingReports.objects.create(
        #             lost_child=child)

        # except FoundChild.DoesNotExist:
        #     return Response({'error': 'No Received Reports Found to Match with'}, status=404)
        # # get image encoding of the child
        # image_encoding = np.array(json.loads(child.image_encoding))

        # # iterate through all reports and check for matching faces

        # for report in queryset:
        #     if report.image_encoding is not None:
        #         report_encoding = np.array(json.loads(report.image_encoding))
        #     else:
        #         report_encoding = None
        #     print(report.child_name)
        #     if child.gender == report.gender:
        #         is_matched, distance = match_results(
        #             image_encoding, report_encoding)
        #         if report_encoding is not None and np.all(is_matched):
        #             try:
        #                 matchingReports_obj.reports.get(
        #                     recieved_child_id=report.id)
        #             except Exception:
        #                 match_obj = {
        #                     "recieved_child": model_to_dict(report),
        #                     "distance": distance
        #                 }
        #                 serialized_report = MatchingChildSerializer(
        #                     data=match_obj)
        #                 serialized_report.is_valid(raise_exception=True)
        #                 if serialized_report.is_valid(raise_exception=True):
        #                     matching_child_obj = serialized_report.save(
        #                         recieved_child=report)
        #                     matchingReports_obj.reports.add(matching_child_obj)

        # # print(model_to_dict(matchingReports_obj))
        # output_data = MatchingReportsSerializer(matchingReports_obj).data
        output_data = createMatches(child)

        return Response(output_data)

class ReceivedChildCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticatedCustom, )
    serializer_class = ReportSerializer

    def post(self, request, format=None):
        request.data['reporter'] = request.user.id
        reportData = request.data
        # reportData["reporter"] = request.user.id
        serializer = self.serializer_class(data=reportData)
        serializer.is_valid(raise_exception=True)
        child = serializer.save()
        if child:
            thread = threading.Thread(target=sendMatchingNotificaitons, args=(child, request.user,))
            thread.start()
            
            return Response(serializer.data)
        else:
            return Response({'message': 'Error Reporting Child'},status=status.HTTP_400_BAD_REQUEST)

class FoundChildCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticatedCustom, )
    serializer_class = ReportSerializer

    def post(self, request, format=None):
        request.data['reporter'] = request.user.id
        reportData = request.data
        # reportData["reporter"] = request.user.id
        serializer = self.serializer_class(data=reportData)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

"""
class UpdateChildStatus(generics.UpdateAPIView):
    serializer_class = ReportSerializer
    channel_layer = get_channel_layer()
    permission_classes = (IsAuthenticatedCustom, )

    def patch(self, request, format=None):
        # get id of the FoundChild or LostChild object
        report_id = request.data.get('report_id', None)

        if not report_id:
            return Response({'error': 'Object report_id not found'}, status=400)
        found_report = FoundChild.objects.get(id=report_id)
        orgUser = User.objects.get(id=request.user.id)
        founder = found_report.reporter
        found_report.reporter = orgUser
        found_report.status = 'received'
        found_report.save()
        child = found_report
        try:
            queryset = LostChild.objects.all()
        except LostChild.DoesNotExist:
            return Response({'error': 'No Lost Reports Found to Match with'}, status=404)
        # get image encoding of the child
        image_encoding = np.array(json.loads(child.image_encoding))

        # iterate through all reports and check for matching faces
        matched_reports = []
        distances = []
        for report in queryset:
            if report.image_encoding is not None:
                report_encoding = np.array(json.loads(report.image_encoding))
            else:
                report_encoding = None
            print(report.child_name)
            if child.gender == report.gender:
                is_matched, distance = match_results(
                    image_encoding, report_encoding)
                if report_encoding is not None and np.all(is_matched):
                    matched_reports.append(report)
                    distances.append(distance)
                    match_obj = {
                        "recieved_child": model_to_dict(child),
                        "distance": distance
                    }
                    serialized_report = MatchingChildSerializer(data=match_obj)
                    if serialized_report.is_valid(raise_exception=True):
                        matching_child_obj = serialized_report.save(
                            recieved_child=child)
                        try:
                            report.matchingReports.reports.add(
                                matching_child_obj)

                            notification = MatchNotification.objects.create(user_id=report.reporter.id,
                                                                            lost_child=report,
                                                                            matching_child_id=matching_child_obj.id, description="Match Report")
                            print(notification)
                            serialized_notification = MatchNotificationSerializer(
                                notification).data
                            print(serialized_notification)
                            async_to_sync(self.channel_layer.group_send)(
                                f"{report.reporter_id}",
                                {
                                    "type": "match_found",
                                    "message": serialized_notification,
                                },
                            )
                        except Exception as e:
                            print(e)
        try:
            drop_notification = DropChildNotification.objects.create(type= "drop_child_success", description="Child is Received Successfully",user = founder, found_child = child  )
            serialized_drop_notification = DropChildNotificationSerializer(drop_notification).data
            async_to_sync(self.channel_layer.group_send)(
                                f"{founder.id}",
                                {
                                    "type": "drop_child_success",
                                    "message": serialized_drop_notification,
                                },
                            )
        except Exception as e:
            return Exception(e)
        serializer = ReportSerializer(matched_reports, many=True)

        output_data = []
        for i, data in enumerate(serializer.data):
            output_data.append({
                'Child': OrderedDict(data.items()),
                'distance': {'distance': distances[i]}
            })

        return Response(output_data)
"""

class LostMatchedReports(APIView):
    channel_layer = get_channel_layer()

    def post(self, request, format=None):
        # get id of the FoundChild or LostChild object
        id = request.data.get('id', None)
        if not id:
            return Response({'error': 'Object id not found'}, status=400)

        try:
            child = LostChild.objects.get(id=id)
            # queryset = FoundChild.objects.all()
            queryset = FoundChild.objects.filter(status='received')
            # try:
            #     matchingReports_obj = child.matchingReports
            # except Exception:
            #     matchingReports_obj = MatchingReports.objects.create(
            #         lost_child=child)

        except FoundChild.DoesNotExist:
            return Response({'error': 'No Received Reports Found to Match with'}, status=404)
        # get image encoding of the child
        image_encoding = np.array(json.loads(child.image_encoding))

        # iterate through all reports and check for matching faces

        for report in queryset:
            if report.image_encoding is not None:
                report_encoding = np.array(json.loads(report.image_encoding))
            else:
                report_encoding = None
            print(report.child_name)
            if child.gender == report.gender:
                is_matched, distance = match_results(
                    image_encoding, report_encoding)
                if report_encoding is not None and np.all(is_matched):
        #             try:
        #                 matchingReports_obj.reports.get(
        #                     recieved_child_id=report.id)
        #             except Exception:
        #                 match_obj = {
        #                     "recieved_child": model_to_dict(report),
        #                     "distance": distance
        #                 }
        #                 serialized_report = MatchingChildSerializer(
        #                     data=match_obj)
        #                 serialized_report.is_valid(raise_exception=True)
        #                 if serialized_report.is_valid(raise_exception=True):
        #                     matching_child_obj = serialized_report.save(
        #                         recieved_child=report)
        #                     matchingReports_obj.reports.add(matching_child_obj)

        # # print(model_to_dict(matchingReports_obj))
        # output_data = MatchingReportsSerializer(matchingReports_obj).data
                    try:
                        matchingChild = MatchingChild.objects.get(recieved_child = report, lost_child = child)
                        print(matchingChild)
                    except MatchingChild.DoesNotExist:
                        MatchingChild.objects.create(recieved_child = report, lost_child = child,
                        distance= distance)
        matching_children = MatchingChild.objects.filter(lost_child = child)
        matched_reports = MatchingChildSerializer(matching_children, many=True).data
        # print (matched_reports)
        return Response(matched_reports)


class GetMatchedReports(APIView):
    permission_classes = (IsAuthenticatedCustom, )
    serializer_class = MatchingChildSerializer

    def post(self, request):
        lost_child = LostChild.objects.get(id=request.data["id"])
        matched_children = MatchingChild.objects.filter(lost_child = lost_child)
        matched_reports = self.serializer_class(matched_children, many=True)

        return Response(matched_reports.data, status=status.HTTP_200_OK)


def image_view(request, child_id):
    
    child = get_object_or_404(Report, id=child_id)

    if child.image:
        with open(child.image.path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/jpeg')

    return HttpResponse('Image not found.')


"""class ReportListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.filter(reporter=request.user)
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            report = Report.objects.get(pk=pk)
            if report.reporter != self.request.user:
                raise PermissionDenied
            return report
        except Report.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        report = self.get_object(pk)
        serializer = ReportSerializer(report)
        return Response(serializer.data)

    def put(self, request, pk):
        report = self.get_object(pk)
        serializer = ReportSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        report = self.get_object(pk)
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)"""


class ReportsByUser(generics.ListAPIView):
    permission_classes = (IsAuthenticatedCustom,)
    serializer_class = ReportSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = {
            "lost_reports": LostChild.objects.filter(reporter=user),
            "found_reports": FoundChild.objects.filter(reporter=user),
            "received_reports": ReceivedChild.objects.filter(reporter=user)
        }
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serialized_data = {}
        for key in queryset:
            serializer = self.serializer_class(queryset[key], many=True)
            serialized_data[key] = serializer.data
        return Response(serialized_data)


class UpdateChildStatus(generics.UpdateAPIView):
    serializer_class = ReportSerializer
    channel_layer = get_channel_layer()
    permission_classes = (IsAuthenticatedCustom, )

    def patch(self, request, format=None):
        report_id = request.data.get('report_id', None)

        if not report_id:
            return Response({'error': 'Object report_id not found'}, status=400)
        try:
            found_report = Report.objects.get(id=report_id)
            # orgUser = User.objects.get(id=request.user.id)
            founder = found_report.reporter
            found_report.reporter = request.user
            found_report.status = Status.Received
            found_report.save()
            child = found_report
            thread = threading.Thread(target=sendMatchingNotificaitons, args=(child, founder,))
            thread.start()
            
            return Response({'message': 'Child Status is successfuly updated'})
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class ReportUpdateAPIView(generics.UpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        old_img = instance.image
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        lostChild = serializer.save()
        if(request.data.get("image")):
            print(request.data)
            lostChild.generate_face_encodings()            
            delete_child_image(old_img.path)


        return Response(serializer.data)

class SearchView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    # permission_classes = (IsAuthenticatedCustom, )

    def get(self, request, *args, **kwargs):

        keyword = kwargs.get('keyword')
        if keyword:
            search_fields = (
                "child_name", "father_name"
            )
            query = self.get_query(keyword, search_fields)
            try:
                results = self.queryset.filter(query)
                serializer = self.serializer_class(results,many=True)
                return Response(serializer.data)
            except Exception as e:
                raise Exception(e)
        return Response("no search results")

    @staticmethod
    def get_query(query_string, search_fields):
        query = None  # Query to search for every search term
        terms = SearchView.normalize_query(query_string)
        for term in terms:
            or_query = None  # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s__icontains" % field_name: term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            if query is None:
                query = or_query
            else:
                query = query & or_query
        return query

    @staticmethod
    def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall, normspace=re.compile(r'\s{2,}').sub):
        return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]
